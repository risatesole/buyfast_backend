from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from products.default.models import Category


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def product_categories_api_view(request: Request) -> Response:
    """
    Read-only endpoint that returns all available product categories.

    Category definitions are centralized in the Category model,
    making the database the single source of truth.
    """
    categories = Category.objects.all().order_by("priority", "name")
    return Response({
        "status": "ok",
        "data": [category.as_dict() for category in categories],
    })
