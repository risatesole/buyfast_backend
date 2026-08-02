# orders/queries.py
from django.db.models import Sum, Count, F, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce


def annotate_order_totals(queryset):
    """
    Adds computed money/count fields to an Order queryset:
      - total_amount: sum of (price_per_item * quantity) across the order's items
      - total_tax:    sum of (tax_amount * quantity) across the order's items
      - item_count:   number of distinct order items

    Shared by the admin orders list view and the admin dashboard summary view
    so both compute order totals the exact same way.
    """
    return queryset.annotate(
        total_amount=Coalesce(
            Sum(ExpressionWrapper(
                F('items__price_per_item') * F('items__quantity'),
                output_field=FloatField()
            )),
            0.0,
            output_field=FloatField()
        ),
        total_tax=Coalesce(
            Sum(ExpressionWrapper(
                F('items__tax_amount') * F('items__quantity'),
                output_field=FloatField()
            )),
            0.0,
            output_field=FloatField()
        ),
        item_count=Count('items', distinct=True),
    )
