from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.utils import CsrfExemptSessionAuthentication

@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
def me_api_view(request):
    try:
        user = request.user

        if not user.is_authenticated:
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
                    }
                }
            })

        return Response({
            "status": "ok",
            "data": {
                "user": {
                    "id": user.id,
                    "firstname": user.first_name,
                    "lastname": user.last_name,
                    "email": user.email,
                    "role": getattr(user, "role", None),
                    "profilepicture": user.profile_picture,
                    "is_authenticated": True,
                    "is_active": user.is_active,
                    "is_staff": user.is_staff,
                    "phone_number": user.phone_number,
                    "matricula": user.matricula,
                    "is_staff": user.is_staff,
                    "permisions": [
                        perm.split(".")[1]
                        for perm in request.user.get_all_permissions()
                        if perm.startswith("accounts.")
                    ]
                }
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
