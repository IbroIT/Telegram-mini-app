from django.core.exceptions import ValidationError
import os


def validate_icon_file(value):
    """
    Валидатор для проверки расширения файла иконки.
    Разрешённые форматы: svg, png, ico, jpeg, jpg
    """
    if value:
        ext = os.path.splitext(value.name)[1].lower()
        valid_extensions = ['.svg', '.png', '.ico', '.jpeg', '.jpg']
        
        if ext not in valid_extensions:
            raise ValidationError(
                f'Неподдерживаемый формат файла. Разрешённые форматы: {", ".join(valid_extensions)}'
            )
