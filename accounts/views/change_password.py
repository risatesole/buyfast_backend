from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.utils import CsrfExemptSessionAuthentication

User = get_user_model()

@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def change_password_api_view(request):
    user = request.user

    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")

    if not old_password or not new_password:
        return Response({
            "status": "error",
            "message": "old_password and new_password are required"
        }, status=400)

    # verify old password
    if not user.check_password(old_password):
        return Response({
            "status": "error",
            "message": "old password is incorrect"
        }, status=400)

    # set new password (IMPORTANT: hashes it properly)
    user.set_password(new_password)
    user.save()

    return Response({
        "status": "ok",
        "message": "password updated successfully"
    })
