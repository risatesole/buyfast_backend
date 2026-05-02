from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

@api_view(['POST'])
def signin_api_view(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response({
            "status": "error",
            "message": "email and password are required"
        }, status=400)

    # IMPORTANT: depends on how your custom user auth works
    user = authenticate(request, username=email, password=password)

    if user is None:
        return Response({
            "status": "error",
            "message": "invalid credentials"
        }, status=401)

    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        "status": "ok",
        "data": {
            "user_id": user.id, # type: ignore
            "email": user.email,
            "role": user.role, # type: ignore
            "token": token.key
        }
    })
