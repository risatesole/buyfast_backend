from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from products.default.models import Product


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def product_categories_api_view(request: Request) -> Response:
    """
    Read-only endpoint that returns all available product categories.

    The category definitions are centralized in Product.Category,
    making the model the single source of truth.
    """
    return Response({
        "status": "ok",
        "data": Product.Category.all(),
    })
