from django.db import models


class City(models.Model):
    """Модель городов для выбора местоположения"""
    name = models.CharField(max_length=100, verbose_name="Название города")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    order = models.IntegerField(default=0, verbose_name="Порядок отображения")
    
    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class DeliveryZone(models.Model):
    """Модель зон доставки с ценами"""
    name = models.CharField(max_length=200, verbose_name="Название зоны")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость доставки ($)", default=0)
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    order = models.IntegerField(default=0, verbose_name="Порядок отображения")
    
    class Meta:
        verbose_name = "Зона доставки"
        verbose_name_plural = "Зоны доставки"
        ordering = ['order', 'name']
    
    def __str__(self):
        if self.price == 0:
            return f"{self.name} (Бесплатно)"
        return f"{self.name} (${self.price})"


class RentalProvider(models.Model):
    """Модель прокатчиков"""
    name = models.CharField(max_length=200, verbose_name="Название прокатчика")
    contact_person = models.CharField(max_length=200, verbose_name="Контактное лицо", blank=True)
    phone = models.CharField(max_length=50, verbose_name="Телефон", blank=True)
    email = models.EmailField(verbose_name="Email", blank=True)
    telegram = models.CharField(max_length=100, verbose_name="Telegram", blank=True)
    terms = models.TextField(verbose_name="Правила проката", blank=True, 
                            help_text="Правила и условия проката от данного прокатчика")
    notes = models.TextField(verbose_name="Заметки", blank=True, 
                            help_text="Внутренние заметки (не видны клиентам)")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Прокатчик"
        verbose_name_plural = "Прокатчики"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ServiceTerms(models.Model):
    """Модель для глобальных правил сервиса"""
    title = models.CharField(max_length=200, verbose_name="Название", default="Правила сервиса")
    content = models.TextField(verbose_name="Текст правил")
    is_active = models.BooleanField(default=True, verbose_name="Активны")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Правила сервиса"
        verbose_name_plural = "Правила сервиса"
    
    def __str__(self):
        return self.title
    
    @classmethod
    def get_active_terms(cls):
        """Получить активные правила сервиса"""
        return cls.objects.filter(is_active=True).first()
