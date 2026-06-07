from ....main.modules.product.services.product.product_service import ProductService
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from src.applications.api.utils import CsrfExemptSessionAuthentication 
from src.applications.main.models import UserRoles
from .handlers.products_handler_get import products_get_handler

@api_view(['GET', 'POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
def products(request):
    service = ProductService()

    if request.method == 'GET':
        return Response(products_get_handler(request))


    user = request.user

    if not user.is_authenticated:
        return Response({"status": "error", "message": "Authentication required"}, status=401)

    if user.role != UserRoles.EMPLOYEE.value:
        return Response({"status": "error", "message": "Only employees can create products"}, status=403)

    try:
        product = service.setProduct(
            name=request.data.get("name"),
            description=request.data.get("description"),
            category_id=request.data.get("category_id"),
            brand=request.data.get("brand"),
            selling_price=request.data.get("selling_price"),
            status=request.data.get("status"),
            tags=request.data.get("tags", []),
        )
    except ValueError as e:
        return Response({"status": "error", "message": str(e)}, status=400)

    return Response({"status": "created", "data": product}, status=201)
