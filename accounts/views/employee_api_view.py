from accounts.accounts import employee_model, EmployeePosition
from accounts.accounts import User, AccountRole
from api.utils import CsrfExemptSessionAuthentication
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET', 'POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def create_employee(request):
    if request.method == 'GET':
        employees = employee_model.objects.select_related('user').all()

        return Response({
            "status": "success",
            "data": [
                {
                    "id": employee.user.id,
                    "email": employee.user.email,
                    "first_name": employee.user.first_name,
                    "last_name": employee.user.last_name,
                    "position": employee.position,
                    "hired_at": employee.hired_at,
                }
                for employee in employees
            ]
        },status=200)

    if request.method == 'POST':
        user = request.user

        if not user.is_authenticated:
            return Response({
                "status": "error",
                "message": "Authentication required"
            }, status=401)

        if user.role != AccountRole.EMPLOYEE.value:
            return Response({
                "status": "error",
                "message": "Only employees can create employee accounts"
            }, status=403)

        email = request.data.get("email")
        password = request.data.get("password")
        first_name = request.data.get("firstname", "")
        last_name = request.data.get("lastname", "")
        position = request.data.get("position", EmployeePosition.STORE_MANAGER)

        if not email or not password:
            return Response({
                "status": "error",
                "message": "Email and password are required"
            }, status=400)

        valid_positions = [choice[0] for choice in EmployeePosition.choices]
        if position and position not in valid_positions:
            return Response({
                "status": "error",
                "message": f"Invalid position. Valid options: {valid_positions}"
            }, status=400)

        if User.objects.filter(email=email).exists():
            return Response({
                "status": "error",
                "message": "A user with this email already exists"
            }, status=409)

        try:
            new_user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=AccountRole.EMPLOYEE.value,
                is_staff=True,
            )

            employee = employee_model.objects.create(
                user=new_user,
                position=position
            )

            return Response({
                "status": "created",
                "data": {
                    "id": new_user.id,
                    "email": new_user.email,
                    "first_name": new_user.first_name,
                    "last_name": new_user.last_name,
                    "position": employee.position,
                    "hired_at": employee.hired_at,
                }
            }, status=201)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=500)