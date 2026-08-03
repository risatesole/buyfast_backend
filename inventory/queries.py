# inventory/queries.py
from django.db.models import Sum, Value, IntegerField
from django.db.models.functions import Coalesce


def get_variant_current_stock(variant_id):
    """
    Returns the current stock for a single variant: the `balance` on its
    most recent StockMovement_model row (0 if it has none yet).

    Shared by the product-status recompute logic so every stock-changing
    endpoint (purchase entry, manual reduction, checkout sale, initial
    inventory) agrees on what "current stock" means for a variant.
    """
    from .models import StockMovement_model

    last_movement = (
        StockMovement_model.objects
        .filter(product_variant_id=variant_id)
        .order_by("-date_time", "-id")
        .first()
    )
    return last_movement.balance if last_movement else 0


def annotate_variant_stock(queryset):
    """
    Adds a computed `total_quantity` field to a ProductVariant queryset, equal
    to the sum of all its stock movement balances (0 if it has none yet).

    Shared by the admin inventory list view and the admin dashboard summary
    view so both compute current stock the exact same way.
    """
    return queryset.annotate(
        total_quantity=Coalesce(
            Sum('stock_movements__balance'),
            Value(0),
            output_field=IntegerField()
        )
    )
