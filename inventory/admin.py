from django.contrib import admin
from .models import StockMovement_model, StockDecrease_model, StockEntry_model

@admin.register(StockMovement_model)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        "product_variant",
        "movement_type",
        "quantity",
        "balance",
        "date_time",
        "document_reference",
    )

    list_filter = (
        "movement_type",
        "date_time",
    )

    search_fields = (
        "product_variant__product__name",
        "product_variant__name",
        "product_variant__sku",
        "document_reference",
    )

    ordering = ("-date_time",)

    readonly_fields = (
        "date_time",
    )


@admin.register(StockEntry_model)
class StockEntryAdmin(admin.ModelAdmin):
    list_display = (
        "stock_movement",
        "created_by",
        "reason",
        "date_time",
    )

    list_filter = (
        "date_time",
    )

    search_fields = (
        "stock_movement__product_variant__product__name",
        "stock_movement__product_variant__sku",
        "created_by__email",
        "reason",
    )

    ordering = ("-date_time",)

    readonly_fields = (
        "date_time",
    )


@admin.register(StockDecrease_model)
class StockDecreaseAdmin(admin.ModelAdmin):
    list_display = (
        "stock_movement",
        "decreased_by",
        "reason",
        "date_time",
    )

    list_filter = (
        "date_time",
    )

    search_fields = (
        "stock_movement__product_variant__product__name",
        "stock_movement__product_variant__sku",
        "decreased_by__email",
        "reason",
    )

    ordering = ("-date_time",)

    readonly_fields = (
        "date_time",
    )
