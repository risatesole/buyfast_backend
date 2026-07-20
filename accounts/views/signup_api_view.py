from django.contrib.auth import login
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.password_validation import validate_password
from accounts.accounts import create_account , AccountRole, AccountStatus
from django.core.mail import send_mail

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
        matricula = request.data.get("matricula")
        terms = request.data.get("terms")

        try:
            validate_password(password)

            user = create_account(first_name,last_name,email,password,AccountRole.CUSTOMER.value,  AccountStatus.ACTIVE.value, matricula,phone_number)
            login(request, user)
            request.META["CSRF_COOKIE_USED"] = True
            send_mail(
                subject="¡Bienvenido al Economato UASD!",
                message=(
                    f"Estimado(a) {user.first_name} {user.last_name},\n\n"
                    "Le damos la bienvenida al Economato UASD!\n\n"
                    "Su cuenta ha sido creada exitosamente y ya puede acceder a nuestros servicios.\n\n"
                    "Información de la cuenta:\n"
                    f"Nombre: {user.first_name} {user.last_name}\n"
                    f"Correo electrónico: {user.email}\n"
                    f"Matrícula: {user.matricula}\n\n"
                    "Si usted no realizó este registro, por favor comuníquese con el equipo de soporte lo antes posible.\n\n"
                    "Atentamente,\n"
                    "Equipo del Economato UASD"
                ),
                from_email=None,  # Usa DEFAULT_FROM_EMAIL
                recipient_list=[user.email],
                fail_silently=False,
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
