from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont
import os
from django.core.files.base import ContentFile
import io

class Category(models.Model):
    title = models.CharField(max_length=100, verbose_name="Название категории")
    icon = models.FileField(upload_to='categories/icons/', verbose_name="Иконка", null=True, blank=True)
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
    
    def __str__(self):
        return self.title

class Feature(models.Model):
    """Модель для особенностей автомобиля"""
    title = models.CharField(max_length=100, verbose_name="Название особенности")
    
    class Meta:
        verbose_name = "Особенность"
        verbose_name_plural = "Особенности"
    
    def __str__(self):
        return self.title

class Car(models.Model):
    OIL_TYPE_CHOICES = [
        ('Бензин', 'Бензин'),
        ('Дизель', 'Дизель'),
        ('Гибрид', 'Гибрид'),
        ('Электричество', 'Электричество'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Свободен'),
        ('booked', 'Забронирован'),
    ]
    
    # Основная информация
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание", blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    features = models.ManyToManyField(Feature, blank=True, verbose_name="Особенности")
    
    # Технические характеристики
    year = models.IntegerField(verbose_name="Год выпуска")
    color = models.CharField(max_length=50, verbose_name="Цвет")
    engine_volume = models.FloatField(verbose_name="Объем двигателя (л)")
    mileage = models.IntegerField(verbose_name="Пробег (км)")
    transmission = models.CharField(max_length=50, verbose_name="Коробка передач", blank=True)
    oil_type = models.CharField(max_length=20, choices=OIL_TYPE_CHOICES, verbose_name="Тип топлива")
    
    # Цены и бронирование
    price_per_day = models.IntegerField(verbose_name="Цена за день ($)")
    deposit = models.IntegerField(verbose_name="Депозит ($)")
    
    # Статус
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name="Статус")
    
    # Системные поля
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"
    
    def __str__(self):
        return f"{self.title} ({self.year})"

class Watermark:
    @staticmethod
    def add_watermark(image_path, watermark_text="RENT CAR"):
        """Добавляет водяной знак на изображение"""
        try:
            # Открываем оригинальное изображение
            image = Image.open(image_path)
            
            # Создаем прозрачный слой для водяного знака
            watermark = Image.new('RGBA', image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark)
            
            # Пытаемся использовать шрифт, если нет - используем стандартный
            try:
                font = ImageFont.truetype("arial.ttf", 80)
            except:
                font = ImageFont.load_default()
            
            # Получаем размеры текста
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Позиционируем текст по центру
            x = (image.width - text_width) // 2
            y = (image.height - text_height) // 2
            
            # Рисуем текст с прозрачностью
            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 80))
            
            # Объединяем изображение с водяным знаком
            watermarked = Image.alpha_composite(image.convert('RGBA'), watermark)
            
            # Конвертируем обратно в RGB если нужно
            if image.mode != 'RGBA':
                watermarked = watermarked.convert('RGB')
            
            # Сохраняем в буфер
            buffer = io.BytesIO()
            watermarked.save(buffer, format='JPEG' if image.format == 'JPEG' else 'PNG')
            buffer.seek(0)
            
            return ContentFile(buffer.read(), name=os.path.basename(image_path))
            
        except Exception as e:
            print(f"Error adding watermark: {e}")
            return None

class CarImage(models.Model):
    car = models.ForeignKey(Car, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='cars/images/')
    order = models.IntegerField(default=0, verbose_name="Порядок")
    
    class Meta:
        ordering = ['order']
        verbose_name = "Фотография автомобиля"
        verbose_name_plural = "Фотографии автомобилей"
    
    def __str__(self):
        return f"Фото {self.car.title}"
    
    def save(self, *args, **kwargs):
        # Сначала сохраняем оригинальное изображение
        super().save(*args, **kwargs)
        
        # Добавляем водяной знак
        if self.image:
            watermarked_image = Watermark.add_watermark(self.image.path)
            if watermarked_image:
                # Сохраняем изображение с водяным знаком
                self.image.save(
                    os.path.basename(self.image.name),
                    watermarked_image,
                    save=False
                )
                super().save(*args, **kwargs)

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('active', 'Активно'),
        ('completed', 'Завершено'),
        ('cancelled', 'Отменено'),
    ]
    
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name="Автомобиль")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    client_name = models.CharField(max_length=200, verbose_name="Имя клиента")
    phone_number = models.CharField(max_length=20, verbose_name="Номер телефона")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус брони")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая стоимость")
    comment = models.TextField(verbose_name="Комментарий", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
    
    def __str__(self):
        return f"{self.car.title} - {self.client_name} ({self.start_date} - {self.end_date})"
    
    @property
    def is_active(self):
        now = timezone.now().date()
        return self.start_date <= now <= self.end_date and self.status in ['confirmed', 'active']
    
    @property
    def total_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0  # или None, если хочешь

    
    def calculate_total_price(self):
        return self.total_days * self.car.price_per_day
    
    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)
