from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont
import os
from django.core.files.base import ContentFile
import io
from watermark import WatermarkProcessor



class ExcursionCategory(models.Model):
    """Категории экскурсий (например: исторические, приключенческие, гастрономические)"""
    title = models.CharField(max_length=100, verbose_name="Название категории")
    icon = models.ImageField(upload_to='excursion_categories/icons/', verbose_name="Иконка", null=True, blank=True)

    class Meta:
        verbose_name = "Категория экскурсии"
        verbose_name_plural = "Категории экскурсий"

    def __str__(self):
        return self.title


class ExcursionFeature(models.Model):
    """Особенности экскурсий (например: групповые, индивидуальные, с гидом)"""
    title = models.CharField(max_length=100, verbose_name="Название особенности")

    class Meta:
        verbose_name = "Особенность экскурсии"
        verbose_name_plural = "Особенности экскурсий"

    def __str__(self):
        return self.title


class Excursion(models.Model):
    STATUS_CHOICES = [
        ('available', 'Доступна'),
        ('booked', 'Забронирована'),
    ]

    # Основная информация
    title = models.CharField(max_length=200, verbose_name="Название экскурсии")
    description = models.TextField(verbose_name="Описание", blank=True)
    category = models.ForeignKey(ExcursionCategory, on_delete=models.CASCADE, verbose_name="Категория")
    features = models.ManyToManyField(ExcursionFeature, blank=True, verbose_name="Особенности")

    # Дни и цены
    days = models.IntegerField(verbose_name="Количество дней", default=1)
    price_per_person = models.IntegerField(verbose_name="Цена за человека ($)")

    # Статус
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name="Статус")

    # Системные поля
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Экскурсия"
        verbose_name_plural = "Экскурсии"

    def __str__(self):
        return self.title


class ExcursionWatermark:
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

class ExcursionImage(models.Model):
    excursion = models.ForeignKey(Excursion, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='excursions/images/')
    order = models.IntegerField(default=0, verbose_name="Порядок")
    
    class Meta:
        ordering = ['order']
        verbose_name = "Фотография экскурсии"
        verbose_name_plural = "Фотографии экскурсий"
    
    def __str__(self):
        return f"Фото {self.excursion.title}"
    
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
                print(f"Error processing watermark for excursion image: {e}")
        
        super().save(*args, **kwargs)


class ExcursionBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('active', 'Активно'),
        ('completed', 'Завершено'),
        ('cancelled', 'Отменено'),
    ]
    
    excursion = models.ForeignKey(Excursion, on_delete=models.CASCADE, verbose_name="Экскурсия")
    telegram_id = models.CharField(max_length=100, verbose_name="Telegram ID")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    client_name = models.CharField(max_length=200, verbose_name="Имя клиента")
    phone_number = models.CharField(max_length=20, verbose_name="Номер телефона")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус брони")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая стоимость")
    comment = models.TextField(verbose_name="Комментарий", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Бронирование экскурсии"
        verbose_name_plural = "Бронирования экскурсий"
    
    def __str__(self):
        return f"{self.excursion.title} - {self.client_name} ({self.start_date} - {self.end_date})"
    
    @property
    def is_active(self):
        now = timezone.now().date()
        return self.start_date <= now <= self.end_date and self.status in ['confirmed', 'active']
    
    @property
    def total_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0 
        
    def calculate_total_price(self):
        return self.total_days * self.excursion.price_per_person
    
    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)
