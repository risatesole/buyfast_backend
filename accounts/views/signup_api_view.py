from django.contrib.auth import login
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError, transaction  # ADD transaction import
from accounts.accounts import create_account, AccountRole, AccountStatus
from accounts.tokens import email_verification_token
from notifications.emailing import send_welcome_email
from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from drf_spectacular.utils import extend_schema
from .signup_api_view_serializer import SignupSerializer
from data_transfer_objects.ErrorResponse import ErrorResponse, ErrorCode

@extend_schema(
    request=SignupSerializer,
    responses={201: SignupSerializer},
)
@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([AllowAny])
@csrf_exempt
def signup_api_view(request):

    if request.method == 'GET':
            # request
            signup_api_view.cls.serializer_class = SignupSerializer

            error = ErrorResponse(
                ErrorCode.EMPTY_BODY,
                "Signup need fields to be filled",
                "error",
                400
            )

            return error.http_response()

    if request.method == 'POST':
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "message": "Validation failed",
                "errors": serializer.errors
            }, status=400)


        first_name = request.data.get("firstname")
        last_name = request.data.get("lastname")
        email = request.data.get("email")
        password = request.data.get("password")
        phone_number = request.data.get("phone")
        matricula = request.data.get("matricula") or None
        terms = request.data.get("terms")

        if terms == None or terms == False:
            return Response({
                "status": "error",
                "message": "Must accept terms of service to signup"
            }, status=400)

        try:
            validate_password(password)

            # USE transaction.atomic() TO PROPERLY HANDLE IntegrityError
            try:
                with transaction.atomic():
                    user = create_account(
                        first_name,
                        last_name,
                        email,
                        password,
                        AccountRole.CUSTOMER.value,
                        AccountStatus.ACTIVE.value,
                        matricula,
                        phone_number
                    )
            except IntegrityError as e:
                # Handle database integrity errors (like duplicate email)
                if 'UNIQUE constraint failed' in str(e) or 'email' in str(e).lower():
                    return Response({
                        "status": "error",
                        "message": "Email already exists",
                        "errors": {"email": ["This email is already registered."]}
                    }, status=400)
                else:
                    # Re-raise if it's a different integrity error
                    raise

            login(request, user)
            request.META["CSRF_COOKIE_USED"] = True

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = email_verification_token.make_token(user)
            verify_link = f"{settings.FRONTEND_URL}/verify-email?uid={uid}&token={token}"

            send_welcome_email(
                to_email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                matricula=user.matricula,
                verify_link=verify_link,
            )

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
                        "phonenumber": user.phone_number,
                        "matricula": user.matricula,
                    },
                    "terms": True
                }
            }, status=201)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=400)
