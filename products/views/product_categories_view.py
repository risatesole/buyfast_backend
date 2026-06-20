from rest_framework.decorators import api_view, authentication_classes, permission_classes
from api.utils import CsrfExemptSessionAuthentication
from ..services.category_service import CategoryService, CategoryAlreadyExistsError
from rest_framework.response import Response
from accounts.accounts import AccountRole

@api_view(['GET', 'POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
def product_categories(request):
    service = CategoryService()

    if request.method == 'GET':
        status = request.query_params.get("status")
        if status == "true":
            status = True
        elif status == "false":
            status = False
        else:
            status = None
        return Response({"status": "ok", "data": service.getCategories(status=status)})

    user = request.user
    if not user.is_authenticated:
        return Response({"status": "error", "message": "Authentication required"}, status=401)
    if user.role != AccountRole.EMPLOYEE.value:
        return Response({"status": "error", "message": "Only employees can create categories"}, status=403)

    try:
        category = service.setCategory(
            name=request.data.get("name"),
            slug=request.data.get("slug"),
            description=request.data.get("description", ""),
            image=request.data.get("image", ""),
            status=request.data.get("status", True),
        )
        return Response({"status": "created", "data": category}, status=201)
    except ValueError as e:
        return Response({"status": "error", "message": str(e)}, status=400)
    except CategoryAlreadyExistsError as e:
        return Response({"status": "error", "message": str(e)}, status=409)
    except Exception as e:
        return Response({"status": "error", "message": "An error occurred while creating the category"}, status=500)
