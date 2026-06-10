from django.contrib.auth import authenticate, login
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
@csrf_exempt
def signin_api_view(request):
    email = request.data.get("email")
    password = request.data.get("password")

    try:
        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response({
                "status": "error",
                "message": "Invalid email or password"
            }, status=401)

        if not user.is_active:
            return Response({
                "status": "error",
                "message": "User account is disabled"
            }, status=403)

        login(request, user)

        request.META["CSRF_COOKIE_USED"] = True

        return Response({
            "status": "ok",
            "message": "signin successful",
            "data": {
                "user": {
                    "id": user.id,
                    "firstname": user.first_name,
                    "lastname": user.last_name,
                    "email": user.email,
                    "role": user.role,
                }
            }
        })

    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=400)
