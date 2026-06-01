from ..main.modules.product.services.product.product_service import ProductService
from ..main.modules.product.models.model_product import Product
from ..main.models import UserRoles
from .utils import CsrfExemptSessionAuthentication
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.views.decorators.csrf import csrf_exempt

@api_view(['GET'])
def health(request):
    return Response({
        "status": "ok"
    })

@api_view(['GET', 'POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def products(request):
    service = ProductService()

    if request.method == 'GET':
        return Response({
            "status": "ok",
            "data": service.getProducts()
        })

    user = request.user

    if not user.is_authenticated:
        return Response({
            "status": "error",
            "message": "Authentication required"
        }, status=401)

    if user.role != UserRoles.EMPLOYEE.value:
        return Response({
            "status": "error",
            "message": "Only employees can create products"
        }, status=403)

    product = service.setProduct(
        name=request.data.get("name"),
        description=request.data.get("description"),
        category=request.data.get("category")
    )

    return Response({
        "status": "created",
        "data": product
    }, status=201)

@api_view(['GET'])
def productcategories(request):
    categories = [
        {
            "value": key,
            "label": label
        }
        for key, label in Product.CATEGORY_CHOICE
    ]
    return Response({
        "status": "ok",
        "data": categories
    })
