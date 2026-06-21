from django.contrib import admin
from .models import CartItem


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "product",
        "quantity",
        "added_at",
        "updated_at",
    )

    list_filter = (
        "added_at",
        "updated_at",
    )

    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "product__name",
    )

    autocomplete_fields = (
        "user",
        "product",
    )

    readonly_fields = (
        "added_at",
        "updated_at",
    )

    ordering = ("-added_at",)
