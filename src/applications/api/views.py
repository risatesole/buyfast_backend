from ..main.modules.product.services.product.product_service import ProductService
from ..main.modules.product.models.model_product import Product
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def health(request):
    return Response({
        "status": "ok"
    })

@api_view(['GET'])
def products(request):
    service = ProductService()
    products = service.getProducts()

    return Response({
        "status": "ok",
        "data": products
    })

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
