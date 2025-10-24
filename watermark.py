# watermark.py
import os
from PIL import Image, ImageDraw, ImageFont
import io
from django.core.files.base import ContentFile
from django.conf import settings

class WatermarkProcessor:
    @staticmethod
    def add_watermark(image_path, opacity=90, scale=0.5):
        """
        Добавляет водяной знак из изображения.
        :param image_path: путь к оригинальному изображению
        :param opacity: прозрачность водяного знака в процентах (0-100)
        :param scale: размер водяного знака относительно ширины изображения (0-1)
        """
        try:
            # Ограничиваем параметры
            opacity = max(0, min(100, opacity)) / 100.0
            scale = max(0.1, min(1.0, scale))  # минимум 10%, максимум 100%
            
            # Путь к водяному знаку
            watermark_path = os.path.join(settings.BASE_DIR, 'media', 'watermark.png')
            if not os.path.exists(watermark_path):
                print(f"Watermark file not found: {watermark_path}")
                return None
            
            # Открываем оригинальное изображение
            original_image = Image.open(image_path)
            image = original_image.convert('RGBA')
            
            # Открываем водяной знак
            watermark = Image.open(watermark_path).convert('RGBA')
            
            # Масштабируем водяной знак по ширине изображения
            image_width, image_height = image.size
            watermark_width = int(image_width * scale)
            watermark_height = int(watermark_width * watermark.height / watermark.width)
            if watermark_width < 100:
                watermark_width = 100
                watermark_height = int(watermark_width * watermark.height / watermark.width)
            
            watermark = watermark.resize((watermark_width, watermark_height), Image.Resampling.LANCZOS)
            
            # Применяем прозрачность
            watermark_with_alpha = Image.new('RGBA', watermark.size)
            for x in range(watermark.width):
                for y in range(watermark.height):
                    r, g, b, a = watermark.getpixel((x, y))
                    watermark_with_alpha.putpixel((x, y), (r, g, b, int(a * opacity)))
            
            # Центрируем водяной знак
            position = ((image_width - watermark_width) // 2, (image_height - watermark_height) // 2)
            
            # Накладываем водяной знак
            watermarked = Image.new('RGBA', image.size)
            watermarked.paste(image, (0, 0))
            watermarked.paste(watermark_with_alpha, position, watermark_with_alpha)
            
            # Конвертируем обратно в исходный формат
            if original_image.mode == 'RGB':
                watermarked = watermarked.convert('RGB')
            
            # Сохраняем в буфер
            buffer = io.BytesIO()
            if original_image.format == 'JPEG':
                watermarked.save(buffer, format='JPEG', quality=95)
            else:
                watermarked.save(buffer, format=original_image.format or 'PNG')
            buffer.seek(0)
            
            return ContentFile(buffer.read(), name=os.path.basename(image_path))
        
        except Exception as e:
            print(f"Error adding watermark: {e}")
            import traceback
            print(traceback.format_exc())
            return None
