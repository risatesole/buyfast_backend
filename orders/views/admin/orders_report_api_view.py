# orders/views/admin/orders_report_api_view.py
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.decorators import api_view, authentication_classes

from api.utils import CsrfExemptSessionAuthentication
from api.permissions import require_permission
from orders.models import Order
from orders.queries import annotate_order_totals, apply_admin_order_filters
from orders.reports_csv import build_orders_report_csv
from orders.reports_pdf import build_orders_report_pdf
from orders.voucher_pdf import STATUS_LABELS_ES
from reports.models import ReportLog


def _build_filters_summary(request):
    parts = []

    status = request.query_params.get("status", "").strip()
    if status:
        parts.append(f"Estado: {STATUS_LABELS_ES.get(status, status)}")

    date_from = request.query_params.get("date_from", "").strip()
    date_to = request.query_params.get("date_to", "").strip()
    if date_from or date_to:
        parts.append(f"Del {date_from or '...'} al {date_to or '...'}")

    search = request.query_params.get("search", "").strip()
    if search:
        parts.append(f'Búsqueda: "{search}"')

    return " · ".join(parts) if parts else "Sin filtros aplicados"


@api_view(["GET"])
@authentication_classes([CsrfExemptSessionAuthentication])
def admin_orders_report_view(request):
    """
    GET /api/v1/admin/reports/orders/

    Same query params as /api/v1/admin/orders/ (search, status, min_total,
    max_total, date_from, date_to, sort), plus:
      ?report_format=  pdf (default) | csv
    (named report_format, not format, since "format" is DRF's reserved
    content-negotiation query param and would otherwise be swallowed by it)
    Returns every matching order, unpaginated, as a downloadable file.
    """
    error = require_permission(request, "orders.view")
    if error:
        return error
    error = require_permission(request, "reports.create")
    if error:
        return error

    qs = Order.objects.select_related("customer").prefetch_related("items").all()
    qs = annotate_order_totals(qs)
    qs = apply_admin_order_filters(qs, request)

    orders = list(qs)
    row_count = len(orders)

    report_format = request.query_params.get("report_format", "pdf").strip().lower()
    if report_format == "csv":
        content = build_orders_report_csv(orders)
        content_type = "text/csv"
        extension = "csv"
    else:
        content = build_orders_report_pdf(orders, _build_filters_summary(request))
        content_type = "application/pdf"
        extension = "pdf"

    ReportLog.objects.create(
        generated_by=request.user,
        report_type="orders",
        format=extension,
        filters={
            key: value
            for key, value in request.query_params.items()
            if key != "report_format"
        },
        row_count=row_count,
    )

    filename = f"reporte-pedidos-{timezone.now().strftime('%Y-%m-%d')}.{extension}"
    response = HttpResponse(content, content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
