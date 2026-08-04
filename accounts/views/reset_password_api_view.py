from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

User = get_user_model()


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
@csrf_exempt
def reset_password_api_view(request):
    uid = request.data.get("uid")
    token = request.data.get("token")
    new_password = request.data.get("new_password")

    if not uid or not token or not new_password:
        return Response({
            "status": "error",
            "message": "uid, token and new_password are required"
        }, status=400)

    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        return Response({
            "status": "error",
            "message": "Invalid or expired password reset link"
        }, status=400)

    if not default_token_generator.check_token(user, token):
        return Response({
            "status": "error",
            "message": "Invalid or expired password reset link"
        }, status=400)

    try:
        validate_password(new_password, user)
    except ValidationError as e:
        return Response({
            "status": "error",
            "message": "Validation failed",
            "errors": {"new_password": e.messages}
        }, status=400)

    user.set_password(new_password)
    user.save()

    return Response({
        "status": "ok",
        "message": "password reset successfully"
    })
