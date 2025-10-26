# core/admin.py или любой существующий admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.admin import ModelAdmin
from unfold.decorators import display
from django.utils.html import format_html
from .models import City, DeliveryZone, RentalProvider, ServiceTerms

# Отменяем стандартную регистрацию
admin.site.unregister(User)
admin.site.unregister(Group)

# Регистрируем с Unfold стилями
@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


@admin.register(City)
class CityAdmin(ModelAdmin):
    list_display = ['name', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    search_fields = ['name']
    list_filter = ['is_active']
    ordering = ['order', 'name']


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(ModelAdmin):
    list_display = ['name', 'price', 'is_active', 'order']
    list_editable = ['price', 'is_active', 'order']
    search_fields = ['name']
    list_filter = ['is_active']
    ordering = ['order', 'name']


@admin.register(RentalProvider)
class RentalProviderAdmin(ModelAdmin):
    list_display = ['name', 'contact_person', 'phone', 'telegram', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'contact_person', 'phone', 'email', 'telegram']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'is_active')
        }),
        ('Контакты', {
            'fields': ('contact_person', 'phone', 'email', 'telegram')
        }),
        ('Правила и условия', {
            'fields': ('terms',),
            'description': 'Правила проката от данного прокатчика. Будут показаны клиенту при бронировании.'
        }),
        ('Внутренние заметки', {
            'fields': ('notes',),
            'classes': ('collapse',),
            'description': 'Эти заметки видны только в админке'
        }),
    )


@admin.register(ServiceTerms)
class ServiceTermsAdmin(ModelAdmin):
    list_display = ['title', 'is_active', 'updated_at']
    list_editable = ['is_active']
    search_fields = ['title', 'content']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'is_active')
        }),
        ('Содержание правил', {
            'fields': ('content',),
            'description': 'Глобальные правила сервиса, которые будут показаны клиенту при бронировании'
        }),
    )
    
    def has_add_permission(self, request):
        # Разрешаем добавлять только если нет активных правил
        if ServiceTerms.objects.filter(is_active=True).exists():
            return False
        return super().has_add_permission(request)
