from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.utils import CsrfExemptSessionAuthentication
from accounts.serializer_helpers import serialize_profile

User = get_user_model()


def _serialize_user(user):
    return {
        "id": user.id,
        "firstname": user.first_name,
        "lastname": user.last_name,
        "email": user.email,
        "role": getattr(user, "role", None),
        "profilepicture": user.profile_picture,
        "is_authenticated": True,
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "is_email_verified": user.is_email_verified,
        "phone_number": user.phone_number,
        "matricula": user.matricula,
        "institutionMember": user.institution_member,
        "permisions": [
            perm.split(".")[1]
            for perm in user.get_all_permissions()
            if perm.startswith("accounts.")
        ],
        "is_superuser": user.is_superuser,
        "profile": serialize_profile(user),
    }


@api_view(['GET', 'PATCH'])
@authentication_classes([CsrfExemptSessionAuthentication])
def me_api_view(request):
    try:
        user = request.user

        if not user.is_authenticated:
            if request.method == 'PATCH':
                return Response({
                    "status": "error",
                    "message": "authentication required"
                }, status=401)

            return Response({
                "status": "ok",
                "data": {
                    "user": {

                        "id": None,
                        "firstname": None,
                        "lastname": None,
                        "email": None,
                        "role": None,
                        "profilepicture": None,
                        "is_authenticated": False,
                        "phone_number": None,
                        "matricula": None,
                        "permisions": None,
                        "is_active": None,
                        "is_staff": None,
                        "is_email_verified": None,
                        "institutionMember": None,
                        "is_superuser": None,
                        "profile": None,
                    }
                }
            })

        if request.method == 'PATCH':
            first_name = request.data.get("first_name")
            if first_name is not None:
                if not isinstance(first_name, str) or not first_name.strip():
                    return Response({
                        "status": "error",
                        "message": "first_name must be a non-empty string"
                    }, status=400)
                user.first_name = first_name.strip()

            last_name = request.data.get("last_name")
            if last_name is not None:
                if not isinstance(last_name, str) or not last_name.strip():
                    return Response({
                        "status": "error",
                        "message": "last_name must be a non-empty string"
                    }, status=400)
                user.last_name = last_name.strip()

            email = request.data.get("email")
            if email is not None:
                if not isinstance(email, str) or not email.strip():
                    return Response({
                        "status": "error",
                        "message": "email must be a non-empty string"
                    }, status=400)

                normalized_email = email.strip().lower()
                if User.objects.filter(email__iexact=normalized_email).exclude(pk=user.pk).exists():
                    return Response({
                        "status": "error",
                        "message": "this email is already in use"
                    }, status=400)

                if normalized_email != user.email:
                    user.is_email_verified = False
                user.email = normalized_email

            user.save()

            return Response({
                "status": "ok",
                "message": "profile updated successfully",
                "data": {
                    "user": _serialize_user(user)
                }
            })

        return Response({
            "status": "ok",
            "data": {
                "user": _serialize_user(user)
            }
        })

    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),
            "data": {
                "user": None
            }
        }, status=400)
