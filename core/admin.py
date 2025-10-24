# core/admin.py или любой существующий admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.admin import ModelAdmin

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