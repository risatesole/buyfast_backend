from django.contrib.auth import get_user_model
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from accounts.tokens import email_verification_token

User = get_user_model()


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
@csrf_exempt
def verify_email_api_view(request):
    uid = request.data.get("uid")
    token = request.data.get("token")

    if not uid or not token:
        return Response({
            "status": "error",
            "message": "uid and token are required"
        }, status=400)

    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        return Response({
            "status": "error",
            "message": "Invalid or expired email verification link"
        }, status=400)

    if user.is_email_verified:
        return Response({
            "status": "ok",
            "message": "email already verified"
        })

    if not email_verification_token.check_token(user, token):
        return Response({
            "status": "error",
            "message": "Invalid or expired email verification link"
        }, status=400)

    user.is_email_verified = True
    user.save()

    return Response({
        "status": "ok",
        "message": "email verified successfully"
    })
