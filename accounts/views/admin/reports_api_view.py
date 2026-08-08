# accounts/views/admin/reports_api_view.py
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.decorators import api_view, authentication_classes

from api.utils import CsrfExemptSessionAuthentication
from api.permissions import require_permission
from accounts.models import User
from accounts.queries import (
    annotate_customer_purchase_count,
    apply_admin_customers_filters,
    apply_admin_employees_filters,
)
from accounts.reports_csv import build_customers_report_csv, build_employees_report_csv
from accounts.reports_pdf import (
    POSITION_LABELS_ES,
    build_customers_report_pdf,
    build_employees_report_pdf,
)
from reports.models import ReportLog


def _employees_filters_summary(request):
    parts = []

    position = request.query_params.get("position", "").strip()
    if position:
        parts.append(f"Posición: {POSITION_LABELS_ES.get(position, position)}")

    date_from = request.query_params.get("date_from", "").strip()
    date_to = request.query_params.get("date_to", "").strip()
    if date_from or date_to:
        parts.append(f"Contratado del {date_from or '...'} al {date_to or '...'}")

    search = request.query_params.get("search", "").strip()
    if search:
        parts.append(f'Búsqueda: "{search}"')

    return " · ".join(parts) if parts else "Sin filtros aplicados"


def _customers_filters_summary(request):
    parts = []

    institution_member = request.query_params.get("institution_member", "").strip()
    if institution_member:
        parts.append("Miembro UASD: " + ("Sí" if institution_member.lower() == "true" else "No"))

    date_from = request.query_params.get("date_from", "").strip()
    date_to = request.query_params.get("date_to", "").strip()
    if date_from or date_to:
        parts.append(f"Registrado del {date_from or '...'} al {date_to or '...'}")

    search = request.query_params.get("search", "").strip()
    if search:
        parts.append(f'Búsqueda: "{search}"')

    return " · ".join(parts) if parts else "Sin filtros aplicados"


def _require_report_access(request, domain_permission):
    error = require_permission(request, domain_permission)
    if error:
        return error
    return require_permission(request, "reports.create")


@api_view(["GET"])
@authentication_classes([CsrfExemptSessionAuthentication])
def admin_employees_report_view(request):
    """
    GET /api/v1/admin/reports/employees/

    Query params:
      ?search=          filter by first/last name or email
      ?position=        filter by employee position (see EmployeePosition)
      ?profile=         filter by access profile id
      ?date_from=       filter by hired_at (YYYY-MM-DD)
      ?date_to=         filter by hired_at (YYYY-MM-DD)
      ?sort=            name | email | hired_at | position (prefix with - for DESC)
      ?report_format=   pdf (default) | csv
    Returns every matching employee, unpaginated, as a downloadable file.
    """
    error = _require_report_access(request, "employees.view")
    if error:
        return error

    qs = User.objects.filter(role="employee").select_related(
        "employee_profile", "employee_profile__profile"
    )
    qs = apply_admin_employees_filters(qs, request)

    employees = list(qs)
    row_count = len(employees)

    report_format = request.query_params.get("report_format", "pdf").strip().lower()
    if report_format == "csv":
        content = build_employees_report_csv(employees)
        content_type = "text/csv"
        extension = "csv"
    else:
        content = build_employees_report_pdf(employees, _employees_filters_summary(request))
        content_type = "application/pdf"
        extension = "pdf"

    ReportLog.objects.create(
        generated_by=request.user,
        report_type="employees",
        format=extension,
        filters={
            key: value
            for key, value in request.query_params.items()
            if key != "report_format"
        },
        row_count=row_count,
    )

    filename = f"reporte-empleados-{timezone.now().strftime('%Y-%m-%d')}.{extension}"
    response = HttpResponse(content, content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@api_view(["GET"])
@authentication_classes([CsrfExemptSessionAuthentication])
def admin_customers_report_view(request):
    """
    GET /api/v1/admin/reports/customers/

    Query params:
      ?search=              filter by first/last name or email
      ?institution_member=  true | false
      ?date_from=            filter by signup date (YYYY-MM-DD)
      ?date_to=              filter by signup date (YYYY-MM-DD)
      ?min_purchases=        minimum number of orders placed
      ?max_purchases=        maximum number of orders placed
      ?sort=                 name | email | created_at | purchases (prefix with - for DESC)
      ?report_format=        pdf (default) | csv
    Returns every matching customer, unpaginated, as a downloadable file.
    """
    error = _require_report_access(request, "customers.view")
    if error:
        return error

    qs = User.objects.filter(role="customer")
    qs = annotate_customer_purchase_count(qs)
    qs = apply_admin_customers_filters(qs, request)

    customers = list(qs)
    row_count = len(customers)

    report_format = request.query_params.get("report_format", "pdf").strip().lower()
    if report_format == "csv":
        content = build_customers_report_csv(customers)
        content_type = "text/csv"
        extension = "csv"
    else:
        content = build_customers_report_pdf(customers, _customers_filters_summary(request))
        content_type = "application/pdf"
        extension = "pdf"

    ReportLog.objects.create(
        generated_by=request.user,
        report_type="customers",
        format=extension,
        filters={
            key: value
            for key, value in request.query_params.items()
            if key != "report_format"
        },
        row_count=row_count,
    )

    filename = f"reporte-clientes-{timezone.now().strftime('%Y-%m-%d')}.{extension}"
    response = HttpResponse(content, content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
