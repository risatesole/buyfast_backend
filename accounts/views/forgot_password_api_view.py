from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from notifications.emailing import send_password_reset_email

User = get_user_model()


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
@csrf_exempt
def forgot_password_api_view(request):
    email = request.data.get("email")

    if not email:
        return Response({
            "status": "error",
            "message": "email is required"
        }, status=400)

    email = email.lower().strip()

    try:
        user = User.objects.get(email=email)

        if user.is_active:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"

            send_password_reset_email(
                to_email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                reset_link=reset_link,
            )
    except User.DoesNotExist:
        pass

    # Always respond ok regardless of whether the email exists, to avoid leaking account existence
    return Response({
        "status": "ok",
        "message": "If an account with that email exists, a password reset link has been sent"
    })
