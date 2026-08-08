# reports/views/report_logs_api_view.py
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response

from api.utils import CsrfExemptSessionAuthentication
from api.permissions import require_superuser
from reports.models import ReportLog


def _serialize_log(log):
    user = log.generated_by
    return {
        "id": log.id,
        "generated_by": {
            "name": f"{user.first_name} {user.last_name}" if user else "Usuario eliminado",
            "email": user.email if user else None,
        },
        "report_type": log.report_type,
        "format": log.format,
        "filters": log.filters,
        "row_count": log.row_count,
        "created_at": log.created_at,
    }


@api_view(["GET"])
@authentication_classes([CsrfExemptSessionAuthentication])
def report_logs_view(request):
    """
    GET /api/v1/admin/reports/logs/

    Superuser-only audit trail of every report generated across all report
    types. Query params:
      ?limit=   max number of results (default 20)
      ?offset=  number of results to skip (default 0)
    """
    error = require_superuser(request)
    if error:
        return error

    qs = ReportLog.objects.select_related("generated_by").all()
    total = qs.count()

    try:
        limit = max(1, int(request.query_params.get("limit", 20)))
    except ValueError:
        limit = 20
    try:
        offset = max(0, int(request.query_params.get("offset", 0)))
    except ValueError:
        offset = 0

    logs = qs[offset: offset + limit]

    return Response({
        "data": [_serialize_log(log) for log in logs],
        "total": total,
    })
