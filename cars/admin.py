# cars/admin.py
from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import Category, Feature, Car, CarImage, Booking, Brand

class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1
    fields = ['image', 'order', 'image_preview']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="60" style="object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return "Нет изображения"
    image_preview.short_description = "Предпросмотр"

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['title', 'icon_preview']
    search_fields = ['title']
    
    @display(description="Иконка")
    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<img src="{}" width="30" height="30" style="object-fit: contain;" />', obj.icon.url)
        return "—"
    icon_preview.short_description = "Иконка"

@admin.register(Feature)
class FeatureAdmin(ModelAdmin):
    list_display = ['title']
    search_fields = ['title']
    list_per_page = 20

@admin.register(Brand)
class BrandAdmin(ModelAdmin):
    list_display = ['name', 'icon_preview']
    search_fields = ['name']
    
    @display(description="Иконка")
    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<img src="{}" width="30" height="30" style="object-fit: contain;" />', obj.icon.url)
        return "—"
    icon_preview.short_description = "Иконка"

@admin.register(Car)
class CarAdmin(ModelAdmin):
    list_display = [
        'title', 'brand', 'category', 'year', 'color', 'status_badge', 
        'price_per_day', 'features_list', 'created_at'
    ]
    list_filter = ['brand', 'category', 'status', 'features', 'year', 'oil_type']
    search_fields = ['title', 'description', 'color', 'transmission', 'brand__name']
    filter_horizontal = ['features']
    inlines = [CarImageInline]
    list_per_page = 20
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('brand', 'title', 'description', 'category', 'status', 'features')
        }),
        ('Технические характеристики', {
            'fields': (
                'year', 'color', 'engine_volume', 'mileage', 
                'transmission', 'oil_type'
            )
        }),
        ('Цены и условия', {
            'fields': (
                'price_per_day', 'deposit'
            )
        }),
    )
    
    @display(description="Особенности")
    def features_list(self, obj):
        features = obj.features.all()[:3]
        features_text = ", ".join([feature.title for feature in features])
        if obj.features.count() > 3:
            features_text += f" ... (+{obj.features.count() - 3})"
        return features_text or "—"
    
    @display(description="Статус")
    def status_badge(self, obj):
        color = "green" if obj.status == 'available' else "orange"
        text = "Свободен" if obj.status == 'available' else "Забронирован"
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color, text
        )

@admin.register(CarImage)
class CarImageAdmin(ModelAdmin):
    list_display = ['car', 'order', 'image_preview']
    list_editable = ['order']
    list_filter = ['car']
    list_per_page = 20
    
    @display(description="Изображение")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="60" style="object-fit: cover; border-radius: 4px;" />', 
                obj.image.url
            )
        return "—"

@admin.register(Booking)
class BookingAdmin(ModelAdmin):
    list_display = [
        'car', 'client_name', 'phone_number', 'start_date', 'end_date', 
        'total_days', 'status_badge', 'total_price', 'created_at'
    ]
    list_filter = ['status', 'start_date', 'end_date', 'car']
    search_fields = ['car__title', 'client_name', 'phone_number', 'telegram_id']
    date_hierarchy = 'start_date'
    readonly_fields = ['total_price', 'total_days', 'created_at']
    list_per_page = 20
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('car', 'client_name', 'phone_number', 'telegram_id')
        }),
        ('Даты бронирования', {
            'fields': ('start_date', 'end_date')
        }),
        ('Статус и стоимость', {
            'fields': ('status', 'total_price', 'total_days')
        }),
        ('Дополнительно', {
            'fields': ('comment', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    @display(description="Дней")
    def total_days(self, obj):
        return obj.total_days
    
    @display(description="Статус")
    def status_badge(self, obj):
        status_colors = {
            'pending': 'gray',
            'confirmed': 'blue', 
            'active': 'green',
            'completed': 'purple',
            'cancelled': 'red'
        }
        status_texts = {
            'pending': 'Ожидание',
            'confirmed': 'Подтверждено',
            'active': 'Активно', 
            'completed': 'Завершено',
            'cancelled': 'Отменено'
        }
        color = status_colors.get(obj.status, 'gray')
        text = status_texts.get(obj.status, obj.status)
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color, text
        )