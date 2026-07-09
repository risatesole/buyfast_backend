from django.contrib import admin
from .models import StockMovement_model

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
