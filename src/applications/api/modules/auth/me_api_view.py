from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ...utils import CsrfExemptSessionAuthentication

@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
def me_api_view(request):
    try:
        user = request.user

        return Response({
            "status": "ok",
            "data": {
                "user": {
                    "id": user.id,
                    "firstname": user.first_name,
                    "lastname": user.last_name,
                    "email": user.email,
                    "role": getattr(user, "role", None),
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
