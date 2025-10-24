from django.contrib import admin
from django.utils.html import format_html
from .models import MotoCategory, MotoFeature, Motorcycle, MotoImage, MotoBooking

class MotoImageInline(admin.TabularInline):
    model = MotoImage
    extra = 1
    fields = ['image', 'order', 'image_preview']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="60" />', obj.image.url)
        return "Нет изображения"
    image_preview.short_description = "Предпросмотр"

@admin.register(MotoCategory)
class MotoCategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'icon_preview']
    search_fields = ['title']
    
    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<img src="{}" width="30" height="30" />', obj.icon.url)
        return "Нет иконки"
    icon_preview.short_description = "Иконка"

@admin.register(MotoFeature)
class MotoFeatureAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']

@admin.register(Motorcycle)
class MotorcycleAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'year', 'color', 'status', 
        'price_per_day', 'bike_type', 'features_list', 'created_at'
    ]
    list_filter = ['category', 'status', 'features', 'year', 'oil_type', 'bike_type']
    search_fields = ['title', 'description', 'color', 'transmission', 'bike_type']
    filter_horizontal = ['features']
    inlines = [MotoImageInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'category', 'status', 'features')
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
    
    def features_list(self, obj):
        return ", ".join([feature.title for feature in obj.features.all()])
    features_list.short_description = "Особенности"

@admin.register(MotoImage)
class MotoImageAdmin(admin.ModelAdmin):
    list_display = ['motorcycle', 'order', 'image_preview']
    list_editable = ['order']
    list_filter = ['motorcycle']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="60" />', obj.image.url)
        return "Нет изображения"
    image_preview.short_description = "Предпросмотр"

@admin.register(MotoBooking)
class MotoBookingAdmin(admin.ModelAdmin):
    list_display = [
        'motorcycle', 'telegram_id', 'client_name', 'phone_number', 'start_date', 'end_date', 
        'total_days', 'status', 'total_price', 'created_at'
    ]
    list_filter = ['status', 'start_date', 'end_date', 'motorcycle']
    search_fields = ['motorcycle__title', 'client_name', 'phone_number', 'telegram_id']
    date_hierarchy = 'start_date'
    readonly_fields = ['total_price', 'total_days']
    
    def total_days(self, obj):
        return obj.total_days
    total_days.short_description = "Дней"
    
    def save_model(self, request, obj, form, change):
        obj.total_price = obj.calculate_total_price()
        super().save_model(request, obj, form, change)