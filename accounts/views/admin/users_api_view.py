from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import Http404

from api.utils import CsrfExemptSessionAuthentication
from api.permissions import require_permission, has_permission
from accounts.models import User, Profile
from .users_api_serializer import UserSerializer


VALID_SORT_FIELDS = {
    "firstname": "first_name",
    "lastname": "last_name",
    "email": "email",
    "status": "status",
    "role": "role",
    "lastLoggedIn": "updated_at",
    "created_at": "created_at",
}


@api_view(["GET", "PATCH"])
@authentication_classes([CsrfExemptSessionAuthentication])
def user_details_api_view(request, id):
    """
        Retrieve or update a user account.

        Endpoint:
            GET   /api/v1/users/<id>/
            PATCH /api/v1/users/<id>/

        Permissions:
            - Requires an authenticated user.
            - Requesting user must have the "employee" role.

        GET:
            Returns the complete user details.

            Response example:
            {
                "success": true,
                "data": {
                    "id": 1,
                    "firstname": "John",
                    "lastname": "Doe",
                    "email": "john@example.com",
                    "matricula": "A12345",
                    "is_active": true,
                    "institutionMember": true,
                    "role": "customer"
                }
            }

        PATCH:
            Updates user account properties.

            Supported fields:

            institution_member:
                - Type: boolean
                - Description: Indicates whether the user belongs to the institution.
                - Example:
                    {
                        "institution_member": true
                    }

            is_active:
                - Type: boolean
                - Description: Controls whether the user can authenticate.
                - Setting this to false disables the account.
                - Example:
                    {
                        "is_active": false
                    }

            matricula:
                - Type: string
                - Description: User's registration number.
                - Example:
                    {
                        "matricula": "B67890"
                    }

            Multiple fields can be updated together:

            Request:
                PATCH /api/v1/users/1/

                {
                    "institution_member": true,
                    "is_active": false,
                    "matricula": "B67890"
                }

            Successful response:
                {
                    "success": true,
                    "message": "User updated successfully.",
                    "data": {
                        ...
                    }
                }

        Errors:
            401:
                Authentication required.

            403:
                Access restricted to employees only.

            404:
                User does not exist.

            400:
                Invalid field type.

                Example:
                {
                    "is_active": "false"
                }

                Response:
                {
                    "success": false,
                    "message": "is_active must be a boolean."
                }
    """
    try:
        user = User.objects.select_related(
            "customer_profile",
            "employee_profile",
        ).get(pk=id)
    except User.DoesNotExist:
        raise Http404("User not found")

    if request.method == "GET":
        required_code = "employees.view" if user.role == "employee" else "customers.view"
    else:  # PATCH
        required_code = "employees.manage" if user.role == "employee" else "customers.manage"
    error = require_permission(request, required_code)
    if error:
        return error

    if request.method == "GET":
        serializer = UserSerializer(user)
        return Response(
            {
                "success": True,
                "data": serializer.data,
            }
        )

    updated = False

    institution_member = request.data.get("institution_member")
    if institution_member is not None:
        if not isinstance(institution_member, bool):
            return Response(
                {
                    "success": False,
                    "message": "institution_member must be a boolean.",
                },
                status=400,
            )

        user.institution_member = institution_member
        updated = True

    is_active = request.data.get("is_active")
    if is_active is not None:
        if not isinstance(is_active, bool):
            return Response(
                {
                    "success": False,
                    "message": "is_active must be a boolean.",
                },
                status=400,
            )

        user.is_active = is_active
        updated = True

    # Soporte para actualizar matrícula
    new_matricula = request.data.get("matricula")
    if new_matricula is not None:
        if not isinstance(new_matricula, str):
            return Response(
                {
                    "success": False,
                    "message": "matricula must be a string.",
                },
                status=400,
            )
        
        if len(new_matricula) > 30:
            return Response(
                {
                    "success": False,
                    "message": "matricula cannot exceed 30 characters.",
                },
                status=400,
            )
        
        # Verificar que la nueva matrícula no exista ya (excepto para este usuario)
        if User.objects.filter(matricula=new_matricula).exclude(pk=user.pk).exists():
            return Response(
                {
                    "success": False,
                    "message": "This matricula is already in use.",
                },
                status=400,
            )
        
        user.matricula = new_matricula
        updated = True

    # Reassign an employee's access profile (e.g. moving someone from Human
    # Resources to Almacen). Only meaningful for employee accounts — customers
    # have no employee_profile/Profile relation.
    new_profile_id = request.data.get("profile")
    if new_profile_id is not None:
        if user.role != "employee":
            return Response(
                {"success": False, "message": "Only employee accounts have an access profile."},
                status=400,
            )

        employee = getattr(user, "employee_profile", None)
        if not employee:
            return Response(
                {"success": False, "message": "Employee record not found for this user."},
                status=400,
            )

        try:
            new_profile = Profile.objects.get(pk=new_profile_id)
        except Profile.DoesNotExist:
            return Response({"success": False, "message": "Invalid profile."}, status=400)

        # Assigning the protected "Superuser" profile hands out every
        # permission code it holds — only an actual superuser may grant that,
        # otherwise an employees.manage holder could self-escalate by
        # reassigning themselves (or anyone) to it.
        if new_profile.is_protected and not request.user.is_superuser:
            return Response(
                {"success": False, "message": "Only a superuser can assign this profile."},
                status=403,
            )

        employee.profile = new_profile
        employee.save()

    if updated:
        user.save()

    serializer = UserSerializer(user)

    return Response(
        {
            "success": True,
            "message": "User updated successfully.",
            "data": serializer.data,
        }
    )


@api_view(["GET"])
@authentication_classes([CsrfExemptSessionAuthentication])
def users(request):
    """
    GET /api/admin/users/

    Query params:
      ?search=      filter by firstname, lastname, or email (case-insensitive)
      ?role=        filter by role: customer | employee (omit to return all)
      ?status=      filter by status: active | deactivated | deleted
      ?sort=        field to sort by: firstname | lastname | email | status |
                    role | lastLoggedIn | created_at (prefix with - for DESC)
      ?limit=       max number of results (default 20)
      ?offset=      number of results to skip (default 0)
    """
    role_filter = request.query_params.get("role", "").strip()
    if role_filter == "employee":
        error = require_permission(request, "employees.view")
    elif role_filter == "customer":
        error = require_permission(request, "customers.view")
    else:
        # Unfiltered listing requires at least one of the two view permissions
        # ("require either", not "require both" — `or` on two Response-or-None
        # results would short-circuit on the first failure and behave as AND).
        if not request.user or not request.user.is_authenticated:
            error = Response({"success": False, "message": "Authentication required."}, status=401)
        elif not (
            has_permission(request.user, "employees.view")
            or has_permission(request.user, "customers.view")
        ):
            error = Response(
                {"success": False, "message": "You do not have permission to perform this action."},
                status=403,
            )
        else:
            error = None
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
        qs = qs.order_by("-created_at")

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
    qs = qs[offset : offset + limit]

    serializer = UserSerializer(qs, many=True)

    return Response(
        {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "data": serializer.data,
        }
    )
