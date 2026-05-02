from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from ....main.modules.account.user.services.user.user_service import UserService, emailExistsError

@api_view(['POST'])
def api_signup_view(request):
    service = UserService()

    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")
    email = request.data.get("email")
    password = request.data.get("password")

    try:
        user, customer = service.createCustomer(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "status": "ok",
            "data": {
                "user_id": user.id,
                "email": user.email,
                "role": user.role,
                "token": token.key
            }
        })

    except emailExistsError as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=400)