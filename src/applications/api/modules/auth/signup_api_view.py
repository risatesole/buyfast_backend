from django.contrib.auth import login
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ....main.modules.account.user.models.model_user import User, UserRoles


@api_view(['POST'])
def signup_api_view(request):
    first_name = request.data.get("firstname")
    last_name = request.data.get("lastname")
    email = request.data.get("email")
    password = request.data.get("password")

    try:
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            role=UserRoles.CUSTOMER.value,
            status="active"
        )

        login(request, user)

        return Response({
            "status": "ok",
            "data": {
                "user": {
                    "id": user.id,
                    "firstname": user.first_name,
                    "lastname": user.last_name,
                    "email": user.email,
                    "role": user.role,
                    "created_at": user.created_at,
                    "modified_at": user.updated_at,
                },
                "terms": True
            }
        })

    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=400)