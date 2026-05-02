from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ....main.modules.product.models.model_product import Product
from ....main.modules.store.services.sell_product import sell_product

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_product(request):
    product_id = request.data.get("product_id")

    if not product_id:
        return Response({
            "status": "error",
            "message": "product_id is required"
        }, status=400)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({
            "status": "error",
            "message": "product not found"
        }, status=404)
    
    try:
        sell_product(product, request.user)

        return Response({
            "status": "ok",
            "message": "product purchased successfully"
        })

    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=500)
