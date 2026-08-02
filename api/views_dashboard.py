# api/views_dashboard.py
from datetime import timedelta

from django.db.models import Count, Sum, F, FloatField, ExpressionWrapper
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response

from api.utils import CsrfExemptSessionAuthentication
from api.permissions import require_employee
from accounts.models import User, employee_model
from orders.models import Order, OrderItem
from orders.queries import annotate_order_totals
from orders.views.admin.serializer import OrderListSerializer
from inventory.models import StockMovement_model
from inventory.queries import annotate_variant_stock
from products.default.models import ProductVariant

DASHBOARD_DAYS = 7           # how many days of history the charts show
LOW_STOCK_THRESHOLD = 5      # products with fewer units than this count as "low stock"
LOW_STOCK_MAX_RESULTS = 20   # cap so the response stays small even with many low-stock items
RECENT_ORDERS_COUNT = 5

# quantity is always stored as a positive number on StockMovement_model;
# the direction (added vs. removed) is implied by movement_type instead.
STOCK_IN_MOVEMENT_TYPES = ["initial_inventory", "purchase_entry"]
STOCK_OUT_MOVEMENT_TYPES = ["customer_sell"]


def _last_n_days(n):
    """Returns a list of the last n calendar dates, oldest first, today included."""
    today = timezone.localdate()
    return [today - timedelta(days=offset) for offset in range(n - 1, -1, -1)]


def _get_order_status_counts():
    counts = {choice_value: 0 for choice_value, _ in Order.Status.choices}
    for row in Order.objects.values("status").annotate(count=Count("id")):
        counts[row["status"]] = row["count"]
    return counts


def _get_low_stock_products():
    variants = (
        annotate_variant_stock(ProductVariant.objects.select_related("product"))
        .filter(status=True, total_quantity__lt=LOW_STOCK_THRESHOLD)
        .order_by("total_quantity")[:LOW_STOCK_MAX_RESULTS]
    )
    return [
        {
            "variant_id": variant.id,
            "product_name": variant.product.name,
            "sku": variant.sku,
            "quantity": variant.total_quantity,
        }
        for variant in variants
    ]


def _get_recent_orders():
    orders = (
        annotate_order_totals(
            Order.objects.select_related("customer").prefetch_related("items")
        )
        .order_by("-created_at")[:RECENT_ORDERS_COUNT]
    )
    return OrderListSerializer(orders, many=True).data


def _get_sales_last_n_days(days):
    """
    Sums order totals (price_per_item * quantity) per day, for orders that
    aren't returned. Returns exactly `days` entries, oldest first, filling in
    0 for days without any orders.
    """
    date_range = _last_n_days(days)
    start_date = date_range[0]

    rows = (
        OrderItem.objects
        .filter(order__created_at__date__gte=start_date)
        .exclude(order__status=Order.Status.RETURNED)
        .annotate(day=TruncDate("order__created_at"))
        .values("day")
        .annotate(
            total=Sum(
                ExpressionWrapper(
                    F("price_per_item") * F("quantity"),
                    output_field=FloatField(),
                )
            )
        )
    )
    totals_by_day = {row["day"]: row["total"] for row in rows}

    return [
        {"date": day.isoformat(), "total": totals_by_day.get(day, 0.0)}
        for day in date_range
    ]


def _get_stock_movements_last_n_days(days):
    """
    Sums stock movement quantity per day, split into stock_in (initial
    inventory + purchase entries) and stock_out (customer sales). Returns
    exactly `days` entries, oldest first, filling in 0 for days without
    movements.
    """
    date_range = _last_n_days(days)
    start_date = date_range[0]

    rows = (
        StockMovement_model.objects
        .filter(date_time__date__gte=start_date)
        .annotate(day=TruncDate("date_time"))
        .values("day", "movement_type")
        .annotate(total_quantity=Sum("quantity"))
    )

    stock_in_by_day = {}
    stock_out_by_day = {}
    for row in rows:
        day = row["day"]
        if row["movement_type"] in STOCK_IN_MOVEMENT_TYPES:
            stock_in_by_day[day] = stock_in_by_day.get(day, 0) + row["total_quantity"]
        elif row["movement_type"] in STOCK_OUT_MOVEMENT_TYPES:
            stock_out_by_day[day] = stock_out_by_day.get(day, 0) + row["total_quantity"]

    return [
        {
            "date": day.isoformat(),
            "stock_in": stock_in_by_day.get(day, 0),
            "stock_out": stock_out_by_day.get(day, 0),
        }
        for day in date_range
    ]


@api_view(["GET"])
@authentication_classes([CsrfExemptSessionAuthentication])
def admin_dashboard_summary_view(request):
    """
    GET /api/v1/admin/dashboard/summary/

    Returns the aggregated data the admin dashboard (/admin) needs in a
    single request: order status counts, employee/customer counts, low
    stock alerts, the most recent orders, and the last 7 days of sales and
    stock movement activity.
    """
    error = require_employee(request)
    if error:
        return error

    data = {
        "order_status_counts": _get_order_status_counts(),
        "employees_count": employee_model.objects.count(),
        "customers_count": User.objects.filter(role="customer").count(),
        "low_stock_products": _get_low_stock_products(),
        "recent_orders": _get_recent_orders(),
        "sales_last_7_days": _get_sales_last_n_days(DASHBOARD_DAYS),
        "stock_movements_last_7_days": _get_stock_movements_last_n_days(DASHBOARD_DAYS),
    }

    return Response({"success": True, "data": data})
