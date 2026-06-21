from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from django.db.models import Q

from api.utils import CsrfExemptSessionAuthentication
from accounts.models import User
from .users_api_serializer import UserSerializer


VALID_SORT_FIELDS = {
    "firstname":   "first_name",
    "lastname":    "last_name",
    "email":       "email",
    "status":      "status",
    "role":        "role",
    "lastLoggedIn": "updated_at",
    "created_at":  "created_at",
}


def _require_employee(request):
    if not request.user or not request.user.is_authenticated:
        return Response({"success": False, "message": "Authentication required."}, status=401)
    if request.user.role != "employee":
        return Response({"success": False, "message": "Access restricted to employees only."}, status=403)
    return None


@api_view(["GET"])
@authentication_classes([CsrfExemptSessionAuthentication])
def users(request):
    """
    GET /api/admin/users/

    Query params:
      ?search=      filter by firstname, lastname, or email (case-insensitive)
      ?role=        filter by role: customer | employee  (omit to return all)
      ?status=      filter by status: active | deactivated | deleted
      ?sort=        field to sort by: firstname | lastname | email | status |
                    role | lastLoggedIn | created_at  (prefix with - for DESC)
      ?limit=       max number of results (default 20)
      ?offset=      number of results to skip (default 0)
    """
    error = _require_employee(request)
    if error:
        return error

    qs = User.objects.select_related("customer_profile").all()

    # --- filters ---
    search = request.query_params.get("search", "").strip()
    if search:
        qs = qs.filter(
            Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
        )

    role = request.query_params.get("role", "").strip()
    if role:
        qs = qs.filter(role=role)

    status = request.query_params.get("status", "").strip()
    if status:
        qs = qs.filter(status=status)

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
    qs = qs[offset: offset + limit]

    serializer = UserSerializer(qs, many=True)
    return Response({
        "success": True,
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": serializer.data,
    })
