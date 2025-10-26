from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont
import os
from django.core.files.base import ContentFile
import io
from watermark import WatermarkProcessor
from core.models import City, DeliveryZone, RentalProvider
class HouseCategory(models.Model):
    title = models.CharField(max_length=100, verbose_name="Название категории")
    icon = models.FileField(upload_to='house_categories/icons/', verbose_name="Иконка", null=True, blank=True)
    
    class Meta:
        verbose_name = "Категория дома"
        verbose_name_plural = "Категории домов"
    
    def __str__(self):
        return self.title

class HouseFeature(models.Model):
    """Модель для особенностей дома"""
    title = models.CharField(max_length=100, verbose_name="Название особенности")
    
    class Meta:
        verbose_name = "Особенность дома"
        verbose_name_plural = "Особенности домов"
    
    def __str__(self):
        return self.title

class House(models.Model):
    STATUS_CHOICES = [
        ('available', 'Свободен'),
        ('booked', 'Забронирован'),
    ]
    
    # Основная информация
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание", blank=True)
    category = models.ForeignKey(HouseCategory, on_delete=models.CASCADE, verbose_name="Категория")
    features = models.ManyToManyField(HouseFeature, blank=True, verbose_name="Особенности")
    
    # Характеристики дома (оставляем только этажи и площадь)
    floors = models.IntegerField(verbose_name="Количество этажей", default=1)
    area = models.FloatField(verbose_name="Площадь (м²)")
    
    # Цены и бронирование (старое поле оставляем для совместимости)
    price_per_day = models.IntegerField(verbose_name="Цена за день ($) (базовая)", help_text="Базовая цена, используется если не заданы тарифы")
    deposit = models.IntegerField(verbose_name="Депозит ($)")
    
    # Новые поля
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Город")
    rental_provider = models.ForeignKey(RentalProvider, on_delete=models.SET_NULL, null=True, blank=True, 
                                       verbose_name="Прокатчик", help_text="Владелец недвижимости")
    delivery_zones = models.ManyToManyField(DeliveryZone, blank=True, verbose_name="Доступные зоны доставки")
    
    # Статус
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name="Статус")
    
    # Системные поля
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Дом"
        verbose_name_plural = "Дома"
    
    def __str__(self):
        return self.title
    
    def get_price_for_days(self, days):
        """Рассчитать цену за указанное количество дней на основе тарифов"""
        tiers = self.price_tiers.filter(is_active=True).order_by('-min_days')
        
        if not tiers.exists():
            return days * self.price_per_day
        
        for tier in tiers:
            if days >= tier.min_days:
                return days * tier.price_per_day
        
        return days * self.price_per_day


class HousePriceTier(models.Model):
    """Модель ценовых тарифов для домов"""
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='price_tiers', verbose_name="Дом")
    min_days = models.IntegerField(verbose_name="Минимум дней", help_text="Минимальное количество дней для применения тарифа")
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за день ($)")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    
    class Meta:
        verbose_name = "Ценовой тариф дома"
        verbose_name_plural = "Ценовые тарифы домов"
        ordering = ['house', 'min_days']
        unique_together = ['house', 'min_days']
    
    def __str__(self):
        return f"{self.house.title} - от {self.min_days} дн. = ${self.price_per_day}/день"

class HouseWatermark:
    @staticmethod
    def add_watermark(image_path, watermark_path='media/watermark.png'):
        """Добавляет водяной знак из изображения"""
        try:
            # Открываем оригинальное изображение
            image = Image.open(image_path).convert('RGBA')
            
            # Открываем водяной знак
            watermark = Image.open(watermark_path).convert('RGBA')
            
            # Масштабируем водяной знак до 50% от размера основного изображения
            image_width, image_height = image.size
            watermark_width = int(image_width * 0.5)
            watermark_height = int(watermark_width * watermark.height / watermark.width)
            
            watermark = watermark.resize((watermark_width, watermark_height), Image.Resampling.LANCZOS)
            
            # Устанавливаем прозрачность водяного знака
            watermark = watermark.copy()
            watermark.putalpha(128)  # 50% прозрачность
            
            # Позиционируем водяной знак по центру
            position = (
                (image_width - watermark_width) // 2,
                (image_height - watermark_height) // 2
            )
            
            # Объединяем изображение с водяным знаком
            watermarked = Image.new('RGBA', image.size)
            watermarked = Image.alpha_composite(watermarked, image)
            watermarked = Image.alpha_composite(watermarked, watermark)
            
            # Конвертируем обратно в RGB если нужно
            watermarked = watermarked.convert('RGB')
            
            # Сохраняем в буфер
            buffer = io.BytesIO()
            watermarked.save(buffer, format='JPEG' if image.format == 'JPEG' else 'PNG')
            buffer.seek(0)
            
            return ContentFile(buffer.read(), name=os.path.basename(image_path))
            
        except Exception as e:
            print(f"Error adding watermark: {e}")
            return None

class HouseImage(models.Model):
    house = models.ForeignKey(House, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='houses/images/')
    order = models.IntegerField(default=0, verbose_name="Порядок")
    
    class Meta:
        ordering = ['order']
        verbose_name = "Фотография дома"
        verbose_name_plural = "Фотографии домов"
    
    def __str__(self):
        return f"Фото {self.house.title}"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
        
        if self.image:
            try:
                watermarked_image = WatermarkProcessor.add_watermark(self.image.path)
                if watermarked_image:
                    self.image.save(
                        os.path.basename(self.image.name),
                        watermarked_image,
                        save=False
                    )
            except Exception as e:
                print(f"Error processing watermark for house image: {e}")
        
        super().save(*args, **kwargs)


class HouseBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('active', 'Активно'),
        ('completed', 'Завершено'),
        ('cancelled', 'Отменено'),
    ]
    
    house = models.ForeignKey(House, on_delete=models.CASCADE, verbose_name="Дом")
    telegram_id = models.CharField(max_length=100, verbose_name="Telegram ID")
    start_date = models.DateField(verbose_name="Дата заезда")
    end_date = models.DateField(verbose_name="Дата выезда")
    client_name = models.CharField(max_length=200, verbose_name="Имя клиента")
    phone_number = models.CharField(max_length=20, verbose_name="Номер телефона")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус брони")
    
    # Новые поля
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Город")
    delivery_zone = models.ForeignKey(DeliveryZone, on_delete=models.SET_NULL, null=True, blank=True, 
                                     verbose_name="Зона доставки")
    
    # Цены
    rental_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость аренды", default=0)
    delivery_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость доставки", default=0)
    deposit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Депозит", default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая стоимость")
    
    # Согласие с правилами
    provider_terms_accepted = models.BooleanField(default=False, verbose_name="Согласие с правилами прокатчика")
    service_terms_accepted = models.BooleanField(default=False, verbose_name="Согласие с правилами сервиса")
    
    comment = models.TextField(verbose_name="Комментарий", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Бронирование дома"
        verbose_name_plural = "Бронирования домов"
    
    def __str__(self):
        return f"{self.house.title} - {self.client_name} ({self.start_date} - {self.end_date})"
    
    @property
    def is_active(self):
        now = timezone.now().date()
        return self.start_date <= now <= self.end_date and self.status in ['confirmed', 'active']
    
    @property
    def total_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0 
    
    def calculate_rental_price(self):
        """Рассчитать стоимость аренды на основе тарифов"""
        return self.house.get_price_for_days(self.total_days)
    
    def calculate_total_price(self):
        """Рассчитать общую стоимость (аренда + доставка)"""
        rental = self.rental_price if self.rental_price else self.calculate_rental_price()
        delivery = self.delivery_price if self.delivery_price else (self.delivery_zone.price if self.delivery_zone else 0)
        return rental + delivery
    
    def save(self, *args, **kwargs):
        if not self.rental_price:
            self.rental_price = self.calculate_rental_price()
        
        if not self.delivery_price and self.delivery_zone:
            self.delivery_price = self.delivery_zone.price
        
        if not self.deposit:
            self.deposit = self.house.deposit
        
        if not self.total_price:
            self.total_price = self.calculate_total_price()
        
        super().save(*args, **kwargs)