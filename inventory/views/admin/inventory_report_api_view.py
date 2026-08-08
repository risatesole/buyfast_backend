# inventory/views/admin/inventory_report_api_view.py
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.decorators import api_view, authentication_classes

from api.utils import CsrfExemptSessionAuthentication
from api.permissions import require_permission
from inventory.models import StockMovement_model
from inventory.queries import (
    annotate_variant_stock,
    apply_admin_inventory_filters,
    apply_admin_stock_movement_filters,
)
from inventory.reports_csv import build_inventory_movements_report_csv, build_inventory_stock_report_csv
from inventory.reports_pdf import (
    INVENTORY_STATUS_LABELS_ES,
    MOVEMENT_TYPE_LABELS_ES,
    build_inventory_movements_report_pdf,
    build_inventory_stock_report_pdf,
)
from products.default.models import ProductVariant
from reports.models import ReportLog


def _stock_filters_summary(request):
    parts = []

    category = request.query_params.get("category", "").strip()
    if category:
        parts.append(f"Categoría: {category}")

    inventory_status = request.query_params.get("inventory_status", "").strip()
    if inventory_status:
        parts.append(f"Estado: {INVENTORY_STATUS_LABELS_ES.get(inventory_status, inventory_status)}")

    search = request.query_params.get("search", "").strip()
    if search:
        parts.append(f'Búsqueda: "{search}"')

    return " · ".join(parts) if parts else "Sin filtros aplicados"


def _movements_filters_summary(request):
    parts = []

    movement_type = request.query_params.get("movement_type", "").strip()
    if movement_type:
        parts.append(f"Tipo: {MOVEMENT_TYPE_LABELS_ES.get(movement_type, movement_type)}")

    date_from = request.query_params.get("date_from", "").strip()
    date_to = request.query_params.get("date_to", "").strip()
    if date_from or date_to:
        parts.append(f"Del {date_from or '...'} al {date_to or '...'}")

    search = request.query_params.get("search", "").strip()
    if search:
        parts.append(f'Búsqueda: "{search}"')

    return " · ".join(parts) if parts else "Sin filtros aplicados"


def _require_inventory_report_access(request):
    error = require_permission(request, "inventory.view")
    if error:
        return error
    return require_permission(request, "reports.create")


@api_view(["GET"])
@authentication_classes([CsrfExemptSessionAuthentication])
def admin_inventory_stock_report_view(request):
    """
    GET /api/v1/admin/reports/inventory/stock/

    Same query params as AdminProductInventoryListView (category, status,
    search, min_quantity, max_quantity, inventory_status, ordering), plus:
      ?report_format=  pdf (default) | csv
    Returns every matching product variant, unpaginated, as a downloadable file.
    """
    error = _require_inventory_report_access(request)
    if error:
        return error

    qs = ProductVariant.objects.select_related("product", "product__category")
    qs = annotate_variant_stock(qs)
    qs = apply_admin_inventory_filters(qs, request)

    variants = list(qs)
    row_count = len(variants)

    report_format = request.query_params.get("report_format", "pdf").strip().lower()
    if report_format == "csv":
        content = build_inventory_stock_report_csv(variants)
        content_type = "text/csv"
        extension = "csv"
    else:
        content = build_inventory_stock_report_pdf(variants, _stock_filters_summary(request))
        content_type = "application/pdf"
        extension = "pdf"

    ReportLog.objects.create(
        generated_by=request.user,
        report_type="inventory_stock",
        format=extension,
        filters={
            key: value
            for key, value in request.query_params.items()
            if key != "report_format"
        },
        row_count=row_count,
    )

    filename = f"reporte-inventario-estado-actual-{timezone.now().strftime('%Y-%m-%d')}.{extension}"
    response = HttpResponse(content, content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@api_view(["GET"])
@authentication_classes([CsrfExemptSessionAuthentication])
def admin_inventory_movements_report_view(request):
    """
    GET /api/v1/admin/reports/inventory/movements/

    Same query params as StockMovementListView's list endpoint (search,
    sort), plus movement_type, date_from, date_to, and:
      ?report_format=  pdf (default) | csv
    Returns every matching stock movement, unpaginated, as a downloadable file.
    """
    error = _require_inventory_report_access(request)
    if error:
        return error

    qs = StockMovement_model.objects.select_related("product_variant", "product_variant__product")
    qs = apply_admin_stock_movement_filters(qs, request)

    movements = list(qs)
    row_count = len(movements)

    report_format = request.query_params.get("report_format", "pdf").strip().lower()
    if report_format == "csv":
        content = build_inventory_movements_report_csv(movements)
        content_type = "text/csv"
        extension = "csv"
    else:
        content = build_inventory_movements_report_pdf(movements, _movements_filters_summary(request))
        content_type = "application/pdf"
        extension = "pdf"

    ReportLog.objects.create(
        generated_by=request.user,
        report_type="inventory_movements",
        format=extension,
        filters={
            key: value
            for key, value in request.query_params.items()
            if key != "report_format"
        },
        row_count=row_count,
    )

    filename = f"reporte-inventario-movimientos-{timezone.now().strftime('%Y-%m-%d')}.{extension}"
    response = HttpResponse(content, content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
