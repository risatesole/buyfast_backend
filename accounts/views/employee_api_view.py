from accounts.accounts import employee_model, EmployeePosition
from accounts.accounts import User, AccountRole
from api.utils import CsrfExemptSessionAuthentication
from api.permissions import require_permission
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET', 'POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def create_employee(request):
    if request.method == 'GET':
        error = require_permission(request, "employees.view")
        if error:
            return error

        employees = employee_model.objects.select_related('user').all()

        return Response({
            "status": "success",
            "data": [
                {
                    "id": employee.user.id,
                    "email": employee.user.email,
                    "first_name": employee.user.first_name,
                    "last_name": employee.user.last_name,
                    "matricula": employee.user.matricula,
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

        error = require_permission(request, "employees.manage")
        if error:
            return error

        email = request.data.get("email")
        password = request.data.get("password")
        first_name = request.data.get("firstname", "")
        last_name = request.data.get("lastname", "")
        position = request.data.get("position", EmployeePosition.STORE_MANAGER)
        matricula = request.data.get("matricula") or None

        profile_id = request.data.get("profile")
        if not profile_id:
            return Response({
                "status": "error",
                "message": "profile is required"
            }, status=400)

        from accounts.models import Profile
        try:
            profile = Profile.objects.get(pk=profile_id)
        except Profile.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Invalid profile"
            }, status=400)

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

        if matricula and User.objects.filter(matricula=matricula).exists():
            return Response({
                "status": "error",
                "message": "A user with this matricula already exists"
            }, status=409)

        try:
            new_user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                matricula=matricula,
                role=AccountRole.EMPLOYEE.value,
                is_staff=True,
            )

            employee = employee_model.objects.create(
                user=new_user,
                position=position,
                profile=profile
            )

            return Response({
                "status": "created",
                "data": {
                    "id": new_user.id,
                    "email": new_user.email,
                    "first_name": new_user.first_name,
                    "last_name": new_user.last_name,
                    "matricula": new_user.matricula,
                    "position": employee.position,
                    "hired_at": employee.hired_at,
                    "profile": {"id": profile.id, "name": profile.name},
                }
            }, status=201)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=500)