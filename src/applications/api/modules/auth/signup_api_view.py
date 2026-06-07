from django.contrib.auth import login
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.password_validation import validate_password
from accounts.accounts import User, UserRoles

@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
@csrf_exempt
def signup_api_view(request):
    first_name = request.data.get("firstname")
    last_name = request.data.get("lastname")
    email = request.data.get("email")
    password = request.data.get("password")
    terms = request.data.get("terms")

    try:
        validate_password(password)
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            role=UserRoles.CUSTOMER.value,
            status="active"
        )

        # 4. Enforce session-based login securely
        login(request, user)

        # 5. Tell Django to skip post-login token validation for this response
        request.META["CSRF_COOKIE_USED"] = True

        return Response({
            "status": "ok",
            "message": "signup successfully",
            "data": {
                "user": {
                    "id": user.id,
                    "firstname": user.first_name,
                    "lastname": user.last_name,
                    "email": user.email,
                    "role": user.role,
                },
                "terms": True
            }
        })

    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=400)
