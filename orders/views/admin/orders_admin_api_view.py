# orders/views/admin_orders_api_view.py
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from django.db.models import Q, Sum, Count, F, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce

from api.utils import CsrfExemptSessionAuthentication
from accounts.models import User
from orders.models import Order, OrderItem, OrderPayment
from .serializer import OrderListSerializer


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


def _require_employee(request):
    if not request.user or not request.user.is_authenticated:
        return Response({"success": False, "message": "Authentication required."}, status=401)
    if request.user.role != "employee":
        return Response({"success": False, "message": "Access restricted to employees only."}, status=403)
    return None


@api_view(["GET"])
@authentication_classes([CsrfExemptSessionAuthentication])
def orders(request):
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
    error = _require_employee(request)
    if error:
        return error

    # Start with base queryset with all related data
    qs = Order.objects.select_related("customer").prefetch_related("items").all()
    
    # Annotate with computed fields
    qs = qs.annotate(
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

    # --- filters ---
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

    # --- sorting ---
    sort_param = request.query_params.get("sort", "-created_at").strip()
    descending = sort_param.startswith("-")
    sort_key = sort_param.lstrip("-")
    db_field = VALID_SORT_FIELDS.get(sort_key)

    if db_field:
        qs = qs.order_by(f"-{db_field}" if descending else db_field)
    else:
        qs = qs.order_by("-created_at")  # fallback

    # --- pagination ---
    try:
        limit = max(1, int(request.query_params.get("limit", 20)))
    except ValueError:
        limit = 20
    try:
        offset = max(0, int(request.query_params.get("offset", 0)))
    except ValueError:
        offset = 0

    total = qs.count()
    
    # Check if there are no orders
    if total == 0:
        return Response({
            "data": {}
        })
    
    qs = qs[offset: offset + limit]

    serializer = OrderListSerializer(qs, many=True)
    return Response({
        "data": serializer.data
    })