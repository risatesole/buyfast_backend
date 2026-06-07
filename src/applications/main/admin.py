# yourapp/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import mark_safe
from .models import Product,Category,User

# ── Status badge helper ────────────────────────────────────────────────────────

def status_badge(obj):
    if obj.status:
        return mark_safe('<span style="color: green; font-weight: bold;">✔ Active</span>')
    return mark_safe('<span style="color: red; font-weight: bold;">✘ Deactivated</span>')

status_badge.short_description = "Status"


def user_status_badge(obj):
    colors = {
        "active": "green",
        "deactivated": "orange",
        "deleted": "red",
    }
    labels = {
        "active": "✔ Active",
        "deactivated": "✘ Deactivated",
        "deleted": "🗑 Deleted",
    }
    color = colors.get(obj.status, "gray")
    label = labels.get(obj.status, obj.status)
    return mark_safe(f'<span style="color: {color}; font-weight: bold;">{label}</span>')

user_status_badge.short_description = "Status"


# ── Category ───────────────────────────────────────────────────────────────────

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", status_badge)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ("status",)


# ── Product ────────────────────────────────────────────────────────────────────

class ProductInline(admin.TabularInline):
    model = Product
    extra = 0
    fields = ("name", "selling_price", "metric_unit")
    show_change_link = True


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "brand", "selling_price", "metric_unit", status_badge)
    list_filter = ("status", "category", "metric_unit")
    search_fields = ("name", "description", "brand")
    list_editable = ("selling_price",)
    ordering = ("name",)
    fieldsets = (
        (None, {
            "fields": ("name", "description", "category", "brand", "image", "tags")
        }),
        ("Pricing & Details", {
            "fields": ("selling_price", "metric_unit", "status")
        }),
    )


# ── User ───────────────────────────────────────────────────────────────────────

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = (
        "email", "first_name", "last_name",
        "role", user_status_badge, "is_staff", "created_at"
    )
    list_filter = ("role", "status", "is_staff", "is_superuser")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "last_login")

    fieldsets = (
        ("Account", {
            "fields": ("email", "password")
        }),
        ("Personal Info", {
            "fields": ("first_name", "last_name")
        }),
        ("Role & Status", {
            "fields": ("role", "status", "is_active", "is_staff", "is_superuser")
        }),
        ("Permissions & Groups", {
            "fields": ("groups", "user_permissions")
        }),
        ("Activity", {
            "fields": ("last_login", "created_at", "updated_at")
        }),
    )

    add_fieldsets = (
        ("Create User", {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "role", "password1", "password2")
        }),
    )

    # username field doesn't exist on this model
    filter_horizontal = ("groups", "user_permissions")