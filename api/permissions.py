from rest_framework.response import Response


def require_employee(request):
    """
    Shared guard for admin-only endpoints.

    Returns a 401/403 Response if the request should be rejected, or None if
    the request is allowed to continue (i.e. the caller is an authenticated
    employee).
    """
    if not request.user or not request.user.is_authenticated:
        return Response(
            {"success": False, "message": "Authentication required."},
            status=401,
        )

    if request.user.role != "employee":
        return Response(
            {"success": False, "message": "Access restricted to employees only."},
            status=403,
        )

    return None
