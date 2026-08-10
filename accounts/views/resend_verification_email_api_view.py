from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response

from api.utils import CsrfExemptSessionAuthentication
from accounts.tokens import email_verification_token
from notifications.emailing import send_verification_email


@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
def resend_verification_email_api_view(request):
    user = request.user

    if not user.is_authenticated:
        return Response({
            "status": "error",
            "message": "authentication required"
        }, status=401)

    if user.is_email_verified:
        return Response({
            "status": "ok",
            "message": "email already verified"
        })

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)
    verify_link = f"{settings.FRONTEND_URL}/verify-email?uid={uid}&token={token}"

    send_verification_email(
        to_email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        verify_link=verify_link,
    )

    return Response({
        "status": "ok",
        "message": "verification email sent"
    })
