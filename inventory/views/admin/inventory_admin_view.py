from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from inventory.models import StockMovement_model
from products.default.models import ProductVariant, Product


class IsEmployee(IsAuthenticated):
    """Custom permission to check if user is an employee"""

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == "employee"


class StockMovementSerializer:
    """Manual serializer for StockMovement data"""

    @staticmethod
    def serialize_product_variant(product_variant):
        """Serialize product variant with full details"""
        product = product_variant.product
        
        # Get category info
        category_info = None
        if hasattr(product, 'category') and product.category:
            # Get the category label from Product.Category.choices
            category_label = dict(Product.Category.choices).get(product.category, "")
            
            category_info = {
                "slug": product.category,
                "label": category_label,
            }
            
            # Add additional category info if available
            if hasattr(Product.Category, 'INFO') and product.category in Product.Category.INFO:
                category_info.update({
                    "description": Product.Category.INFO[product.category].get("description", ""),
                    "priority": Product.Category.INFO[product.category].get("priority", 0),
                })
        
        # Get images from the variant's images
        variant_images = []
        if hasattr(product_variant, "images"):
            variant_images = [
                {
                    "url": img.image if isinstance(img.image, str) else img.image.url,
                    "type": img.image_type or "HERO",
                    "alt_text": img.alt_text or "",
                    "order": img.order,
                }
                for img in product_variant.images.all().order_by('order')
            ]
        
        # If no variant images, try to get from product's thumbnail
        if not variant_images and hasattr(product, 'thumbnail') and product.thumbnail:
            variant_images = [{
                "url": product.thumbnail,
                "type": "HERO",
                "alt_text": product.name,
                "order": 0,
            }]

        return {
            "id": product_variant.id,
            "name": product_variant.name,
            "description": product_variant.description or "",
            "variant_number": product_variant.variantnumber,
            "slug": product_variant.slug,
            "sku": product_variant.sku,
            "status": product_variant.status,
            "selling_price": float(product_variant.selling_price) if product_variant.selling_price else 0,
            "tax_rate": float(product_variant.tax_rate) if product_variant.tax_rate else 0,
            "product": {
                "id": product.id,
                "name": product.name,
                "slug": product.slug,
                "category": category_info,
                "product_type": product.product_type,
                "product_type_label": dict(Product.ProductType.choices).get(product.product_type, ""),
                "thumbnail": product.thumbnail or "",
                "tags": list(product.tags.values_list("name", flat=True)) if hasattr(product, "tags") else [],
                "created_at": product.created_at.isoformat() if product.created_at else None,
                "updated_at": product.updated_at.isoformat() if product.updated_at else None,
            },
            "images": variant_images,
            "created_at": product_variant.created_at.isoformat() if product_variant.created_at else None,
            "updated_at": product_variant.updated_at.isoformat() if product_variant.updated_at else None,
        }

    @staticmethod
    def serialize_stock_movement(movement):
        """Serialize a single stock movement"""
        return {
            "id": movement.id,
            "date_time": movement.date_time.isoformat(),
            "product_variant": StockMovementSerializer.serialize_product_variant(movement.product_variant),
            "movement_type": movement.movement_type,
            "movement_type_label": dict(StockMovement_model.MOVEMENT_TYPES).get(movement.movement_type, ""),
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

    def get(self, request, movement_id=None):
        """
        Handle both list and detail views
        - If movement_id is provided, return specific movement
        - Otherwise, return paginated list
        """
        try:
            # If movement_id is provided, return detail view
            if movement_id is not None:
                return self.get_detail(request, movement_id)
            
            # Otherwise, return list view
            return self.get_list(request)
            
        except ValueError as e:
            return Response(
                {"status": "error", "message": f"Invalid query parameters: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            import traceback
            print(f"Error in StockMovementListView: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get_detail(self, request, movement_id):
        """Get a single stock movement by ID"""
        # Get the movement with all related data
        movement = get_object_or_404(
            StockMovement_model.objects.select_related(
                "product_variant",
                "product_variant__product"
            ).prefetch_related(
                "product_variant__images"
            ),
            id=movement_id
        )
        
        # Serialize the movement
        serialized_data = StockMovementSerializer.serialize_stock_movement(movement)
        
        return Response(
            {
                "status": "ok",
                "data": serialized_data,
            },
            status=status.HTTP_200_OK,
        )

    def get_list(self, request):
        """Get paginated list of stock movements"""
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

        # Build queryset with proper select_related for variant and product
        queryset = StockMovement_model.objects.select_related(
            "product_variant",
            "product_variant__product"
        ).prefetch_related(
            "product_variant__images"
        )

        # Apply search filter if provided
        if search:
            queryset = queryset.filter(
                Q(product_variant__product__name__icontains=search)
                | Q(product_variant__name__icontains=search)
                | Q(document_reference__icontains=search)
                | Q(product_variant__sku__icontains=search)
                | Q(product_variant__product__slug__icontains=search)
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

        # Return response
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