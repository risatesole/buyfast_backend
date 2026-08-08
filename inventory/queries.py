# inventory/queries.py
from django.db.models import Q, Sum, Value, IntegerField
from django.db.models.functions import Coalesce

INVENTORY_ORDERING_FIELDS = [
    'name', 'sku', 'total_quantity', 'created_at', 'selling_price',
    '-name', '-sku', '-total_quantity', '-created_at', '-selling_price',
]

STOCK_MOVEMENT_SORT_FIELDS = [
    'date_time', '-date_time', 'quantity', '-quantity',
    'balance', '-balance', 'movement_type', '-movement_type',
]


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


def apply_admin_inventory_filters(queryset, request):
    """
    Applies the admin inventory list's category/status/search/quantity/
    inventory_status filters and ordering to a ProductVariant queryset
    (expects annotate_variant_stock to have already been applied for the
    total_quantity filters/ordering).

    Shared by the paginated admin inventory list view (AdminProductInventoryListView)
    and the (unpaginated) admin inventory report/export view, so both filter
    variants identically.
    """
    category = request.query_params.get('category')
    if category:
        queryset = queryset.filter(product__category__slug=category)

    status_param = request.query_params.get('status')
    if status_param is not None:
        status_bool = status_param.lower() == 'true'
        queryset = queryset.filter(status=status_bool)

    search = request.query_params.get('search')
    if search:
        queryset = queryset.filter(
            Q(product__name__icontains=search) |
            Q(name__icontains=search) |
            Q(sku__icontains=search)
        )

    min_quantity = request.query_params.get('min_quantity')
    if min_quantity:
        queryset = queryset.filter(total_quantity__gte=int(min_quantity))

    max_quantity = request.query_params.get('max_quantity')
    if max_quantity:
        queryset = queryset.filter(total_quantity__lte=int(max_quantity))

    inventory_status = request.query_params.get('inventory_status')
    if inventory_status:
        if inventory_status == 'out_of_stock':
            queryset = queryset.filter(total_quantity=0)
        elif inventory_status == 'low_stock':
            queryset = queryset.filter(total_quantity__gt=0, total_quantity__lte=10)
        elif inventory_status == 'medium_stock':
            queryset = queryset.filter(total_quantity__gt=10, total_quantity__lte=50)
        elif inventory_status == 'in_stock':
            queryset = queryset.filter(total_quantity__gt=50)

    ordering = request.query_params.get('ordering', '-created_at')
    if ordering in INVENTORY_ORDERING_FIELDS:
        queryset = queryset.order_by(ordering)
    else:
        queryset = queryset.order_by('-created_at')

    return queryset


def apply_admin_stock_movement_filters(queryset, request):
    """
    Applies the admin stock movement list's search/sort filters, plus
    movement_type/date_from/date_to filters, to a StockMovement_model
    queryset.

    Shared by the paginated admin stock movement list view
    (StockMovementListView.get_list) and the (unpaginated) admin inventory
    movements report/export view, so both filter movements identically.
    """
    search = request.query_params.get('search', '').strip()
    if search:
        queryset = queryset.filter(
            Q(product_variant__product__name__icontains=search)
            | Q(product_variant__name__icontains=search)
            | Q(document_reference__icontains=search)
            | Q(product_variant__sku__icontains=search)
            | Q(product_variant__product__slug__icontains=search)
        )

    movement_type = request.query_params.get('movement_type', '').strip()
    if movement_type:
        queryset = queryset.filter(movement_type=movement_type)

    date_from = request.query_params.get('date_from', '').strip()
    if date_from:
        queryset = queryset.filter(date_time__date__gte=date_from)

    date_to = request.query_params.get('date_to', '').strip()
    if date_to:
        queryset = queryset.filter(date_time__date__lte=date_to)

    sort = request.query_params.get('sort', '-date_time')
    if sort in STOCK_MOVEMENT_SORT_FIELDS:
        queryset = queryset.order_by(sort)
    else:
        queryset = queryset.order_by('-date_time')

    return queryset
