from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import User

class CustomUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    model = User

    list_display = ("email", "first_name", "last_name", "role", "status", "is_staff", "is_active")
    list_filter = ("role", "status", "is_staff", "is_active")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

    fieldsets = (
        ("Credentials", {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("role", "status", "is_staff", "is_active", "is_superuser")}),
    )

    add_fieldsets = (
        ("Credentials", {
            "fields": ("email", "password1", "password2")
        }),
        ("Personal Info", {
            "fields": ("first_name", "last_name")
        }),
        ("Permissions", {
            "fields": ("role", "status", "is_staff", "is_active", "is_superuser")
        }),
    )

admin.site.register(User, CustomUserAdmin)