from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont
import os
from django.core.files.base import ContentFile
import io


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
    def add_watermark(image_path, watermark_text="EXCURSION"):
        """Добавляет водяной знак на изображение"""
        try:
            image = Image.open(image_path)
            watermark = Image.new('RGBA', image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark)

            try:
                font = ImageFont.truetype("arial.ttf", 60)
            except:
                font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            x = (image.width - text_width) // 2
            y = (image.height - text_height) // 2

            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 60))

            watermarked = Image.alpha_composite(image.convert('RGBA'), watermark)
            if image.mode != 'RGBA':
                watermarked = watermarked.convert('RGB')

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
        super().save(*args, **kwargs)
        if self.image:
            watermarked_image = ExcursionWatermark.add_watermark(self.image.path)
            if watermarked_image:
                self.image.save(
                    os.path.basename(self.image.name),
                    watermarked_image,
                    save=False
                )
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
        return (self.end_date - self.start_date).days + 1
    
    def calculate_total_price(self):
        return self.total_days * self.excursion.price_per_person
    
    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('active', 'Активно'),
        ('completed', 'Завершено'),
        ('cancelled', 'Отменено'),
    ]

    excursion = models.ForeignKey(Excursion, on_delete=models.CASCADE, verbose_name="Экскурсия")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь Telegram")

    # исправлено: добавлены значения по умолчанию для дат
    start_date = models.DateField(verbose_name="Дата начала", default=timezone.now)
    end_date = models.DateField(verbose_name="Дата окончания", default=timezone.now)

    client_name = models.CharField(max_length=200, verbose_name="Имя клиента", default="Unknown")
    phone_number = models.CharField(max_length=20, verbose_name="Номер телефона", default="Не указан")
    participants = models.IntegerField(verbose_name="Количество участников", default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус брони")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая стоимость", default=0)
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
        return (self.end_date - self.start_date).days + 1

    def calculate_total_price(self):
        return self.participants * self.excursion.price_per_person * self.total_days

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)
