# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    User,
    Customer_model,
    employee_model,
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        "email",
        "first_name",
        "last_name",
        "role",
        "status",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "role",
        "status",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
    )

    ordering = ("email",)

    fieldsets = (
        (None, {
            "fields": ("email", "password")
        }),
        ("Personal Info", {
            "fields": ("first_name", "last_name")
        }),
        ("Account", {
            "fields": ("role", "status")
        }),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Important Dates", {
            "fields": ("last_login",)
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "first_name",
                "last_name",
                "password1",
                "password2",
                "role",
                "status",
                "is_active",
                "is_staff",
            ),
        }),
    )


@admin.register(Customer_model)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "phone",
        "created_at",
    )

    search_fields = (
        "user__email",
        "phone",
    )


@admin.register(employee_model)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "position",
        "is_active",
        "hired_at",
    )

    list_filter = (
        "position",
        "is_active",
    )

    search_fields = (
        "user__email",
        "position",
    )