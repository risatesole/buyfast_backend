from django.conf import settings
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response

from api.utils import CsrfExemptSessionAuthentication
from accounts.tokens import email_verification_token


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

    send_mail(
        subject="Verifica tu correo - Economato UASD",
        message=(
            f"Estimado(a) {user.first_name} {user.last_name},\n\n"
            "Para poder completar compras en el Economato UASD, primero debe verificar "
            "su correo electrónico.\n\n"
            f"Para verificar su cuenta, visite el siguiente enlace:\n{verify_link}\n\n"
            "Si usted no solicitó este correo, puede ignorarlo.\n\n"
            "Atentamente,\n"
            "Equipo del Economato UASD"
        ),
        from_email=None,  # Usa DEFAULT_FROM_EMAIL
        recipient_list=[user.email],
        fail_silently=False,
    )

    return Response({
        "status": "ok",
        "message": "verification email sent"
    })
