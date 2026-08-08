# orders/views/admin_orders_api_view.py
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response

from api.utils import CsrfExemptSessionAuthentication
from api.permissions import require_permission
from accounts.models import User
from orders.models import Order, OrderItem, OrderPayment
from orders.queries import annotate_order_totals, apply_admin_order_filters
from .serializer import OrderListSerializer


@api_view(["GET"])
@authentication_classes([CsrfExemptSessionAuthentication])
def admin_order_view(request):
    """
    GET /api/admin/orders/

    Query params:
      ?search=      filter by customer firstname, lastname, or email (case-insensitive)
      ?status=      filter by status: pending | fulfilled | returned
      ?min_total=   minimum order total
      ?max_total=   maximum order total
      ?date_from=   filter orders created after this date (YYYY-MM-DD)
      ?date_to=     filter orders created before this date (YYYY-MM-DD)
      ?sort=        field to sort by: id | firstname | lastname | email | 
                    created_at | total | pickup_time | status
                    (prefix with - for DESC)
      ?limit=       max number of results (default 20)
      ?offset=      number of results to skip (default 0)
    """
    error = require_permission(request, "orders.view")
    if error:
        return error

    # Start with base queryset with all related data
    qs = Order.objects.select_related("customer").prefetch_related("items").all()

    # Annotate with computed fields (shared helper, see orders/queries.py)
    qs = annotate_order_totals(qs)

    # --- filters + sorting (shared with the admin orders report/export view) ---
    qs = apply_admin_order_filters(qs, request)

    # Total count of matching rows BEFORE pagination is applied.
    # Must be computed here (on the filtered/annotated qs, before slicing)
    # so it reflects the full result set, not just the current page.
    total = qs.count()

    # --- pagination ---
    try:
        limit = max(1, int(request.query_params.get("limit", 20)))
    except ValueError:
        limit = 20
    try:
        offset = max(0, int(request.query_params.get("offset", 0)))
    except ValueError:
        offset = 0

    # Always return the same shape, even when there are no results,
    # so the frontend doesn't have to special-case an empty {}.
    if total == 0:
        return Response({"data": [], "total": 0})

    qs = qs[offset: offset + limit]

    serializer = OrderListSerializer(qs, many=True)
    return Response({
        "data": serializer.data,
        "total": total,
    })
