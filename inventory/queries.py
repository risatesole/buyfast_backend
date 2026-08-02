# inventory/queries.py
from django.db.models import Sum, Value, IntegerField
from django.db.models.functions import Coalesce


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
