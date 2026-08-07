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


def has_permission(user, code):
    """Core RBAC check. Superuser bypasses everything. No profile => no access."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    employee = getattr(user, "employee_profile", None)
    if not employee or not employee.profile:
        return False
    return code in employee.profile.permissions


def require_permission(request, code):
    """Function-view guard mirroring require_employee's response shape."""
    if not request.user or not request.user.is_authenticated:
        return Response({"success": False, "message": "Authentication required."}, status=401)
    if not has_permission(request.user, code):
        return Response(
            {"success": False, "message": "You do not have permission to perform this action."},
            status=403,
        )
    return None


def permission_required(code):
    """DRF permission-class factory for class-based views."""
    from rest_framework.permissions import BasePermission

    class _HasPermission(BasePermission):
        def has_permission(self, request, view):
            return has_permission(request.user, code)

    return _HasPermission


def require_superuser(request):
    """Guard for profile-management endpoints (superuser-only, not permission-code-gated)."""
    if not request.user or not request.user.is_authenticated:
        return Response({"success": False, "message": "Authentication required."}, status=401)
    if not request.user.is_superuser:
        return Response({"success": False, "message": "Superuser access required."}, status=403)
    return None
