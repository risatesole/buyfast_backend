from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from inventory.models import StockMovement_model
from products.models import Product  # Adjust import based on your structure


class IsEmployee(IsAuthenticated):
    """Custom permission to check if user is an employee"""

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == "employee"


class StockMovementSerializer:
    """Manual serializer for StockMovement data"""

    @staticmethod
    def serialize_product(product):
        """Serialize product with full details"""
        return {
            "id": product.id,
            "name": product.name,
            "description": product.description or "",
            "brand": product.brand or "",
            "selling_price": float(product.selling_price)
            if product.selling_price
            else 0,
            "status": product.status,
            "category": {
                "id": product.category.id,
                "name": product.category.name,
                "slug": product.category.slug,
                "image": product.category.image or "",
                "status": product.category.status,
            }
            if product.category
            else None,
            "images": [
                {
                    "url": img.image.url
                    if hasattr(img.image, "url")
                    else str(img.image),
                    "type": img.image_type or "HERO",
                }
                for img in product.productimage_set.all()
            ]
            if hasattr(product, "productimage_set")
            else [],
            "tags": list(product.tags.values_list("name", flat=True))
            if hasattr(product, "tags")
            else [],
        }

    @staticmethod
    def serialize_stock_movement(movement):
        """Serialize a single stock movement"""
        return {
            "id": movement.id,
            "date_time": movement.date_time.isoformat(),
            "product": StockMovementSerializer.serialize_product(movement.product),
            "movement": {"type": movement.movement_type},
            "quantity": movement.quantity,
            "balance": movement.balance,
            "document_reference": movement.document_reference or "",
        }


class StockMovementListView(APIView):
    """
    API endpoint for listing stock movements
    Endpoint: GET /api/v1/admin/inventory/stockmovement
    Only accessible by employees
    """

    permission_classes = [IsEmployee]

    def get(self, request):
        try:
            # Get query parameters
            limit = int(request.query_params.get("limit", 10))
            offset = int(request.query_params.get("offset", 0))
            search = request.query_params.get("search", "").strip()
            sort = request.query_params.get(
                "sort", "-date_time"
            )  # Default: newest first

            # Validate pagination parameters
            limit = max(1, min(limit, 100))  # Min 1, Max 100
            offset = max(0, offset)

            # Build queryset
            queryset = StockMovement_model.objects.select_related("product")

            # Apply search filter if provided
            if search:
                queryset = queryset.filter(
                    Q(product__name__icontains=search)
                    | Q(document_reference__icontains=search)
                    | Q(product__description__icontains=search)
                )

            # Apply sorting
            # Validate sort field to prevent SQL injection
            allowed_sort_fields = [
                "date_time",
                "-date_time",
                "quantity",
                "-quantity",
                "balance",
                "-balance",
                "movement_type",
                "-movement_type",
            ]
            if sort in allowed_sort_fields:
                queryset = queryset.order_by(sort)
            else:
                queryset = queryset.order_by("-date_time")

            # Get total count for pagination info
            total_count = queryset.count()

            # Apply pagination
            paginated_items = queryset[offset : offset + limit]

            # Serialize data
            serialized_data = [
                StockMovementSerializer.serialize_stock_movement(item)
                for item in paginated_items
            ]

            # Return response matching Mockoon format
            return Response(
                {
                    "status": "ok",
                    "data": serialized_data,
                    "pagination": {
                        "limit": limit,
                        "offset": offset,
                        "total": total_count,
                        "has_next": (offset + limit) < total_count,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response(
                {"status": "error", "message": "Invalid query parameters"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
