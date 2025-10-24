from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Feature, Car, CarImage, Booking

class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1
    fields = ['image', 'order', 'image_preview']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="60" />', obj.image.url)
        return "Нет изображения"
    image_preview.short_description = "Предпросмотр"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'icon_preview']
    search_fields = ['title']
    
    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<img src="{}" width="30" height="30" />', obj.icon.url)
        return "Нет иконки"
    icon_preview.short_description = "Иконка"

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'year', 'color', 'status', 
        'price_per_day', 'features_list', 'created_at'
    ]
    list_filter = ['category', 'status', 'features', 'year', 'oil_type']
    search_fields = ['title', 'description', 'color', 'transmission']
    filter_horizontal = ['features']
    inlines = [CarImageInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'category', 'status', 'features')
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
    
    def features_list(self, obj):
        return ", ".join([feature.title for feature in obj.features.all()])
    features_list.short_description = "Особенности"

@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ['car', 'order', 'image_preview']
    list_editable = ['order']
    list_filter = ['car']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="60" />', obj.image.url)
        return "Нет изображения"
    image_preview.short_description = "Предпросмотр"

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'car', 'client_name', 'phone_number', 'start_date', 'end_date', 
        'total_days', 'status', 'total_price', 'created_at'
    ]
    list_filter = ['status', 'start_date', 'end_date', 'car']
    search_fields = ['car__title', 'client_name', 'phone_number', 'user__username']
    date_hierarchy = 'start_date'
    readonly_fields = ['total_price', 'total_days']
    
    def total_days(self, obj):
        return obj.total_days
    total_days.short_description = "Дней"
    
    def save_model(self, request, obj, form, change):
        obj.total_price = obj.calculate_total_price()
        super().save_model(request, obj, form, change)