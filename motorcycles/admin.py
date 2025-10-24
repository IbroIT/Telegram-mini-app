# motorcycles/admin.py
from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import MotoCategory, MotoFeature, Motorcycle, MotoImage, MotoBooking, MotoBrand

class MotoImageInline(admin.TabularInline):
    model = MotoImage
    extra = 1
    fields = ['image', 'order', 'image_preview']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="60" style="object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return "Нет изображения"
    image_preview.short_description = "Предпросмотр"

@admin.register(MotoCategory)
class MotoCategoryAdmin(ModelAdmin):
    list_display = ['title', 'icon_preview']
    search_fields = ['title']
    
    @display(description="Иконка")
    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<img src="{}" width="30" height="30" style="object-fit: contain;" />', obj.icon.url)
        return "—"

@admin.register(MotoFeature)
class MotoFeatureAdmin(ModelAdmin):
    list_display = ['title']
    search_fields = ['title']
    list_per_page = 20

@admin.register(MotoBrand)
class MotoBrandAdmin(ModelAdmin):
    list_display = ['name', 'icon_preview']
    search_fields = ['name']
    
    @display(description="Иконка")
    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<img src="{}" width="30" height="30" style="object-fit: contain;" />', obj.icon.url)
        return "—"
    icon_preview.short_description = "Иконка"

@admin.register(Motorcycle)
class MotorcycleAdmin(ModelAdmin):
    list_display = [
        'title', 'brand', 'category', 'year', 'color', 'status_badge', 
        'price_per_day', 'bike_type', 'features_list', 'created_at'
    ]
    list_filter = ['brand', 'category', 'status', 'features', 'year', 'oil_type', 'bike_type']
    search_fields = ['title', 'description', 'color', 'transmission', 'bike_type', 'brand__name']
    filter_horizontal = ['features']
    inlines = [MotoImageInline]
    list_per_page = 20
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('brand', 'title', 'description', 'category', 'status', 'features')
        }),
        ('Технические характеристики', {
            'fields': (
                'year', 'color', 'engine_volume', 'mileage', 
                'transmission', 'oil_type', 'bike_type', 'power'
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

@admin.register(MotoImage)
class MotoImageAdmin(ModelAdmin):
    list_display = ['motorcycle', 'order', 'image_preview']
    list_editable = ['order']
    list_filter = ['motorcycle']
    list_per_page = 20
    
    @display(description="Изображение")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="60" style="object-fit: cover; border-radius: 4px;" />', 
                obj.image.url
            )
        return "—"

@admin.register(MotoBooking)
class MotoBookingAdmin(ModelAdmin):
    list_display = [
        'motorcycle', 'client_name', 'phone_number', 'start_date', 'end_date', 
        'total_days', 'status_badge', 'total_price', 'created_at'
    ]
    list_filter = ['status', 'start_date', 'end_date', 'motorcycle']
    search_fields = ['motorcycle__title', 'client_name', 'phone_number', 'telegram_id']
    date_hierarchy = 'start_date'
    readonly_fields = ['total_price', 'total_days', 'created_at']
    list_per_page = 20
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('motorcycle', 'client_name', 'phone_number', 'telegram_id')
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