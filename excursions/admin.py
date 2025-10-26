# excursions/admin.py
from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import ExcursionCategory, ExcursionFeature, Excursion, ExcursionImage, ExcursionBooking, ExcursionPriceTier

class ExcursionImageInline(admin.TabularInline):
    model = ExcursionImage
    extra = 1
    fields = ['image', 'order', 'image_preview']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="60" style="object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return "Нет изображения"
    image_preview.short_description = "Предпросмотр"


class ExcursionPriceTierInline(admin.TabularInline):
    model = ExcursionPriceTier
    extra = 1
    fields = ['min_participants', 'price_per_person', 'is_active']
    ordering = ['min_participants']

@admin.register(ExcursionCategory)
class ExcursionCategoryAdmin(ModelAdmin):
    list_display = ['title', 'icon_preview']
    search_fields = ['title']
    
    @display(description="Иконка")
    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<img src="{}" width="30" height="30" style="object-fit: contain;" />', obj.icon.url)
        return "—"

@admin.register(ExcursionFeature)
class ExcursionFeatureAdmin(ModelAdmin):
    list_display = ['title']
    search_fields = ['title']
    list_per_page = 20

@admin.register(Excursion)
class ExcursionAdmin(ModelAdmin):
    list_display = [
        'title', 'category', 'city', 'rental_provider_name', 'days', 'status_badge', 
        'price_per_person', 'features_list', 'created_at'
    ]
    list_filter = ['category', 'city', 'rental_provider', 'status', 'features', 'days']
    search_fields = ['title', 'description']
    filter_horizontal = ['features', 'delivery_zones']
    inlines = [ExcursionPriceTierInline, ExcursionImageInline]
    list_per_page = 20
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'category', 'status', 'features')
        }),
        ('Местоположение и организатор', {
            'fields': ('city', 'rental_provider', 'delivery_zones')
        }),
        ('Дни и цены', {
            'fields': ('days', 'price_per_person', 'deposit'),
            'description': 'Базовая цена используется когда не заданы тарифы. Добавьте тарифы ниже для гибкого ценообразования.'
        }),
    )
    
    @display(description="Организатор")
    def rental_provider_name(self, obj):
        return obj.rental_provider.name if obj.rental_provider else "—"
    
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
        text = "Доступна" if obj.status == 'available' else "Забронирована"
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color, text
        )

@admin.register(ExcursionImage)
class ExcursionImageAdmin(ModelAdmin):
    list_display = ['excursion', 'order', 'image_preview']
    list_editable = ['order']
    list_filter = ['excursion']
    list_per_page = 20
    
    @display(description="Изображение")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="60" style="object-fit: cover; border-radius: 4px;" />', 
                obj.image.url
            )
        return "—"

@admin.register(ExcursionBooking)
class ExcursionBookingAdmin(ModelAdmin):
    list_display = [
        'excursion', 'client_name', 'phone_number', 'participants', 'city', 'delivery_zone_name',
        'start_date', 'end_date', 'total_days', 'status_badge', 
        'excursion_price', 'transfer_price', 'total_price', 'provider_name', 'created_at'
    ]
    list_filter = ['status', 'city', 'delivery_zone', 'start_date', 'end_date', 'excursion', 'excursion__rental_provider']
    search_fields = ['excursion__title', 'client_name', 'phone_number', 'telegram_id']
    date_hierarchy = 'start_date'
    readonly_fields = ['excursion_price', 'transfer_price', 'deposit', 'total_price', 'total_days', 'created_at']
    list_per_page = 20
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('excursion', 'client_name', 'phone_number', 'telegram_id', 'participants')
        }),
        ('Местоположение и трансфер', {
            'fields': ('city', 'delivery_zone')
        }),
        ('Даты бронирования', {
            'fields': ('start_date', 'end_date')
        }),
        ('Стоимость', {
            'fields': ('excursion_price', 'transfer_price', 'deposit', 'total_price', 'total_days'),
            'description': 'Цены рассчитываются автоматически на основе тарифов'
        }),
        ('Согласие с правилами', {
            'fields': ('provider_terms_accepted', 'service_terms_accepted')
        }),
        ('Статус и дополнительно', {
            'fields': ('status', 'comment', 'created_at'),
        }),
    )
    
    @display(description="Дней")
    def total_days(self, obj):
        return obj.total_days
    
    @display(description="Зона трансфера")
    def delivery_zone_name(self, obj):
        return obj.delivery_zone.name if obj.delivery_zone else "—"
    
    @display(description="Организатор")
    def provider_name(self, obj):
        return obj.excursion.rental_provider.name if obj.excursion.rental_provider else "—"
    
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