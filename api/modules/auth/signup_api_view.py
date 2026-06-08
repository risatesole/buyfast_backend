from django.contrib.auth import login
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.password_validation import validate_password
from accounts.accounts import create_account , AccountRole, AccountStatus

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
        
        user = create_account(first_name,last_name,email,password,AccountRole.CUSTOMER.value,  AccountStatus.ACTIVE.value)
        login(request, user)
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
        }, status=201)

    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=400)
