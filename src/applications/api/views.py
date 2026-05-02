from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def health(request):
    return Response({
        "status": "ok"
    })

from ..main.modules.product.services.product.product_service import ProductService

@api_view(['GET'])
def products(request):
    service = ProductService()
    products = service.getProducts()

    return Response({
        "status": "ok",
        "data": products
    })
