from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from django.db.models import ProtectedError

from api.utils import CsrfExemptSessionAuthentication
from api.permissions import require_superuser, require_permission, has_permission
from accounts.models import Profile, PERMISSION_CATALOG, PERMISSION_CODES


def _require_profile_list_access(request):
    """
    GET (listing available profiles) is needed both by the superuser-only
    profile-management page and by anyone who can create/reassign employees
    (they need the list to populate a profile picker) — so GET is allowed for
    employees.manage holders too, not just superusers. Creating/editing/
    deleting profile *definitions* stays superuser-only (see require_superuser
    below), since that changes what a whole profile grants everyone on it.
    """
    if not request.user or not request.user.is_authenticated:
        return Response({"success": False, "message": "Authentication required."}, status=401)
    if not (request.user.is_superuser or has_permission(request.user, "employees.manage")):
        return Response(
            {"success": False, "message": "You do not have permission to perform this action."},
            status=403,
        )
    return None


def _serialize_profile(profile):
    return {
        "id": profile.id,
        "name": profile.name,
        "description": profile.description,
        "permissions": profile.permissions,
        "is_protected": profile.is_protected,
        "employee_count": profile.employees.count(),
    }


def _catalog_meta():
    return [{"code": code, "label": label} for code, label in PERMISSION_CATALOG]


def _validate_permissions(codes):
    if not isinstance(codes, list) or not all(isinstance(c, str) for c in codes):
        return "permissions must be a list of strings"
    unknown = [c for c in codes if c not in PERMISSION_CODES]
    if unknown:
        return f"Unknown permission code(s): {unknown}"
    return None


@api_view(["GET", "POST"])
@authentication_classes([CsrfExemptSessionAuthentication])
def profiles_list_view(request):
    if request.method == "GET":
        error = _require_profile_list_access(request)
        if error:
            return error

        profiles = Profile.objects.all().order_by("name")
        return Response({
            "success": True,
            "data": [_serialize_profile(p) for p in profiles],
            "meta": {"permission_catalog": _catalog_meta()},
        })

    # POST — creating a new profile definition is superuser-only
    error = require_superuser(request)
    if error:
        return error

    name = request.data.get("name", "").strip()
    description = request.data.get("description", "")
    permissions = request.data.get("permissions", [])

    if not name:
        return Response({"success": False, "message": "name is required"}, status=400)
    err = _validate_permissions(permissions)
    if err:
        return Response({"success": False, "message": err}, status=400)
    if Profile.objects.filter(name=name).exists():
        return Response({"success": False, "message": "A profile with this name already exists"}, status=409)

    profile = Profile.objects.create(name=name, description=description, permissions=permissions)
    return Response({"success": True, "data": _serialize_profile(profile)}, status=201)


@api_view(["GET", "PATCH", "DELETE"])
@authentication_classes([CsrfExemptSessionAuthentication])
def profile_detail_view(request, id):
    error = require_superuser(request)
    if error:
        return error

    try:
        profile = Profile.objects.get(pk=id)
    except Profile.DoesNotExist:
        return Response({"success": False, "message": "Profile not found"}, status=404)

    if request.method == "GET":
        return Response({"success": True, "data": _serialize_profile(profile)})

    if request.method == "PATCH":
        if profile.is_protected:
            return Response({"success": False, "message": "This profile cannot be modified."}, status=400)

        name = request.data.get("name")
        if name is not None:
            name = name.strip()
            if not name:
                return Response({"success": False, "message": "name cannot be empty"}, status=400)
            if Profile.objects.filter(name=name).exclude(pk=profile.pk).exists():
                return Response({"success": False, "message": "A profile with this name already exists"}, status=409)
            profile.name = name

        description = request.data.get("description")
        if description is not None:
            profile.description = description

        permissions = request.data.get("permissions")
        if permissions is not None:
            err = _validate_permissions(permissions)
            if err:
                return Response({"success": False, "message": err}, status=400)
            profile.permissions = permissions

        profile.save()
        return Response({"success": True, "data": _serialize_profile(profile)})

    # DELETE
    if profile.is_protected:
        return Response({"success": False, "message": "This profile cannot be deleted."}, status=400)
    employee_count = profile.employees.count()
    if employee_count > 0:
        return Response(
            {"success": False, "message": f"Cannot delete a profile assigned to {employee_count} employee(s)."},
            status=400,
        )
    try:
        profile.delete()
    except ProtectedError:
        return Response({"success": False, "message": "This profile is still assigned to employees."}, status=400)
    return Response({"success": True, "message": "Profile deleted."})
