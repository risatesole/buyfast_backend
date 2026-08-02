from django.db import transaction
from django.db.models import Q
from django.http import Http404
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

class IsInventory(IsAuthenticated):
    """Custom permission to check if user is inventory staff"""

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
        if product.category:
            category_info = {
                "slug": product.category.slug,
                "label": product.category.name,
                "description": product.category.description,
                "priority": product.category.priority,
            }
        
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
    API endpoint for listing and creating stock movements
    - GET  /api/v1/admin/inventory/stockmovement          -> list / detail (employees)
    - POST /api/v1/admin/inventory/stockmovement           -> create purchase entry (inventory staff)
    """

    def get_permissions(self):
        """
        Use different permission classes depending on the HTTP method:
        - GET requires the user to be an employee
        - POST requires the user to be inventory staff
        """
        if self.request.method == "POST":
            return [IsInventory()]
        return [IsEmployee()]

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

    def post(self, request):
        """
        Add stock to inventory via a purchase entry.

        Expects JSON body:
            {
                "sku": "<product variant sku>",
                "quantity": <positive int>,
                "document_reference": "<optional string>"
            }

        Only accessible by users with role == "inventory" (see IsInventory).
        Creates a StockMovement_model row with movement_type="purchase_entry",
        with balance computed as the previous balance for that variant + quantity.
        """
        sku = request.data.get("sku")
        quantity = request.data.get("quantity")
        document_reference = request.data.get("document_reference", "")

        # Validate presence of required fields
        if not sku:
            return Response(
                {"status": "error", "message": "sku is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if quantity is None:
            return Response(
                {"status": "error", "message": "quantity is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate quantity is a positive integer
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response(
                {"status": "error", "message": "quantity must be an integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if quantity <= 0:
            return Response(
                {"status": "error", "message": "quantity must be greater than zero"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                # Lock the product variant row to avoid race conditions on balance calc
                product_variant = get_object_or_404(
                    ProductVariant.objects.select_for_update(),
                    sku=sku,
                )

                # Lock and fetch the most recent movement for this variant
                last_movement = (
                    StockMovement_model.objects
                    .select_for_update()
                    .filter(product_variant=product_variant)
                    .order_by("-date_time", "-id")
                    .first()
                )
                current_balance = last_movement.balance if last_movement else 0
                new_balance = current_balance + quantity

                movement = StockMovement_model.objects.create(
                    product_variant=product_variant,
                    movement_type="purchase_entry",
                    quantity=quantity,
                    balance=new_balance,
                    document_reference=document_reference,
                )

            serialized_data = StockMovementSerializer.serialize_stock_movement(movement)

            return Response(
                {"status": "ok", "data": serialized_data},
                status=status.HTTP_201_CREATED,
            )

        except Http404:
            return Response(
                {"status": "error", "message": f"Product variant with sku '{sku}' not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            import traceback
            print(f"Error in StockMovementListView.post: {str(e)}")
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
