from django.contrib.auth import logout
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.utils import CsrfExemptSessionAuthentication  

@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def signout_api_view(request):
    try:
        logout(request)
        return Response({
            "status": "ok",
            "message": "signout successful"
        })
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=400)