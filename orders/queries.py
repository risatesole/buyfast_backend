# orders/queries.py
from django.db.models import Q, Sum, Count, F, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce

VALID_SORT_FIELDS = {
    "id": "id",
    "firstname": "customer__first_name",
    "lastname": "customer__last_name",
    "email": "customer__email",
    "created_at": "created_at",
    "total": "total_amount",
    "pickup_time": "pickup_time",
    "status": "status",
}


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


def apply_admin_order_filters(qs, request):
    """
    Applies the admin order list's search/status/total/date filters and
    sort order to an Order queryset (expects annotate_order_totals to have
    already been applied for the total_amount sort field).

    Shared by the paginated admin orders list view and the (unpaginated)
    admin orders report/export view, so both filter orders identically.
    """
    search = request.query_params.get("search", "").strip()
    if search:
        qs = qs.filter(
            Q(customer__first_name__icontains=search)
            | Q(customer__last_name__icontains=search)
            | Q(customer__email__icontains=search)
        )

    status = request.query_params.get("status", "").strip()
    if status:
        qs = qs.filter(status=status)

    min_total = request.query_params.get("min_total", "").strip()
    if min_total:
        try:
            qs = qs.filter(total_amount__gte=float(min_total))
        except ValueError:
            pass

    max_total = request.query_params.get("max_total", "").strip()
    if max_total:
        try:
            qs = qs.filter(total_amount__lte=float(max_total))
        except ValueError:
            pass

    date_from = request.query_params.get("date_from", "").strip()
    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)

    date_to = request.query_params.get("date_to", "").strip()
    if date_to:
        qs = qs.filter(created_at__date__lte=date_to)

    sort_param = request.query_params.get("sort", "-created_at").strip()
    descending = sort_param.startswith("-")
    sort_key = sort_param.lstrip("-")
    db_field = VALID_SORT_FIELDS.get(sort_key)

    if db_field:
        qs = qs.order_by(f"-{db_field}" if descending else db_field)
    else:
        qs = qs.order_by("-created_at")  # fallback

    return qs
