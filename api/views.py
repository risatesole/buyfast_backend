from products.products import ProductService
from accounts.accounts import AccountRole
from .utils import CsrfExemptSessionAuthentication
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def set_product_price(request):
    user = request.user

    if user.role != AccountRole.EMPLOYEE.value:
        return Response({"status": "error", "message": "Only employees can update product prices"}, status=403)

    service = ProductService()

    product = service.setProductPrice(
        product_id=request.data.get("product_id"),
        selling_price=request.data.get("selling_price")
    )

    if product is None:
        return Response({"status": "error", "message": "Product not found"}, status=404)

    return Response({"status": "ok", "data": product})

