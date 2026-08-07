from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from django.db.models import Sum, Q
from products.default.models import ProductVariant
from inventory.models import StockMovement_model
from inventory.serializers import ProductInventorySerializer
from inventory.queries import annotate_variant_stock
from api.permissions import permission_required

class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class CustomLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 20
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 100

class AdminProductInventoryListView(generics.ListAPIView):
    """
    Admin view to list all products with their inventory quantities.
    Shows product name, description, thumbnail, and current quantity.
    
    Query Parameters:
    - category: Filter by product category
    - status: Filter by variant status (true/false)
    - search: Search by product name, variant name, or SKU
    - min_quantity: Filter by minimum quantity
    - max_quantity: Filter by maximum quantity
    - inventory_status: Filter by inventory status (in_stock, low_stock, out_of_stock, medium_stock)
    - ordering: Order by field (name, sku, quantity, created_at, selling_price)
    - page: Page number (for page-based pagination)
    - page_size: Number of items per page (for page-based pagination)
    - offset: Number of items to skip (for offset-based pagination)
    - limit: Number of items to return (for offset-based pagination)
    """
    serializer_class = ProductInventorySerializer
    pagination_class = CustomLimitOffsetPagination
    permission_classes = [permission_required("inventory.view")]

    def get_queryset(self):
        # Annotate with total quantity
        queryset = ProductVariant.objects.all().select_related('product').prefetch_related('images')
        
        # Annotate with quantity for filtering and ordering (shared helper, see inventory/queries.py)
        queryset = annotate_variant_stock(queryset)
        
        # Filter by product category if provided
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(product__category__slug=category)
        
        # Filter by status (active/inactive)
        status_param = self.request.query_params.get('status')
        if status_param is not None:
            status_bool = status_param.lower() == 'true'
            queryset = queryset.filter(status=status_bool)
        
        # Filter by search term
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(product__name__icontains=search) |
                Q(name__icontains=search) |
                Q(sku__icontains=search)
            )
        
        # Filter by min/max quantity
        min_quantity = self.request.query_params.get('min_quantity')
        max_quantity = self.request.query_params.get('max_quantity')
        
        if min_quantity:
            queryset = queryset.filter(total_quantity__gte=int(min_quantity))
        if max_quantity:
            queryset = queryset.filter(total_quantity__lte=int(max_quantity))
        
        # Filter by inventory status
        inventory_status = self.request.query_params.get('inventory_status')
        if inventory_status:
            if inventory_status == 'out_of_stock':
                queryset = queryset.filter(total_quantity=0)
            elif inventory_status == 'low_stock':
                queryset = queryset.filter(total_quantity__gt=0, total_quantity__lte=10)
            elif inventory_status == 'medium_stock':
                queryset = queryset.filter(total_quantity__gt=10, total_quantity__lte=50)
            elif inventory_status == 'in_stock':
                queryset = queryset.filter(total_quantity__gt=50)
        
        # Order by
        ordering = self.request.query_params.get('ordering', '-created_at')
        allowed_orderings = ['name', 'sku', 'total_quantity', 'created_at', 'selling_price', '-name', '-sku', '-total_quantity', '-created_at', '-selling_price']
        
        if ordering in allowed_orderings:
            # Handle ordering by total_quantity
            if ordering == 'total_quantity' or ordering == '-total_quantity':
                queryset = queryset.order_by(ordering)
            else:
                queryset = queryset.order_by(ordering)
        
        return queryset

class AdminProductInventoryDetailView(generics.RetrieveUpdateAPIView):
    """
    Admin view to get and update inventory details for a specific product variant.
    """
    queryset = ProductVariant.objects.all().select_related('product').prefetch_related('images')
    serializer_class = ProductInventorySerializer
    lookup_field = 'pk'

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH"):
            return [permission_required("products.edit")()]
        return [permission_required("inventory.view")()]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Update variant status if provided
        if 'status' in request.data:
            instance.status = request.data['status']
            instance.save()
        
        # Update selling price if provided
        if 'selling_price' in request.data:
            instance.selling_price = request.data['selling_price']
            instance.save()
        
        return super().update(request, *args, **kwargs)

class AdminLowStockView(generics.ListAPIView):
    """
    Admin view to list products with low stock (quantity below threshold).
    
    Query Parameters:
    - threshold: Stock threshold (default: 10)
    - offset: Number of items to skip
    - limit: Number of items to return
    """
    serializer_class = ProductInventorySerializer
    pagination_class = CustomLimitOffsetPagination
    permission_classes = [permission_required("inventory.view")]

    def get_queryset(self):
        threshold = int(self.request.query_params.get('threshold', 10))
        
        # Get all variants with their stock quantities
        variants = ProductVariant.objects.all().select_related('product').prefetch_related('images')
        
        # Filter those with stock below threshold
        low_stock_variants = []
        for variant in variants:
            quantity = self.get_variant_quantity(variant)
            if 0 < quantity < threshold:
                low_stock_variants.append(variant)
        
        return low_stock_variants
    
    def get_variant_quantity(self, variant):
        total = StockMovement_model.objects.filter(
            product_variant=variant
        ).aggregate(total=Sum('balance'))['total']
        return total if total is not None else 0

class AdminOutOfStockView(generics.ListAPIView):
    """
    Admin view to list products that are out of stock.
    
    Query Parameters:
    - offset: Number of items to skip
    - limit: Number of items to return
    """
    serializer_class = ProductInventorySerializer
    pagination_class = CustomLimitOffsetPagination
    permission_classes = [permission_required("inventory.view")]

    def get_queryset(self):
        variants = ProductVariant.objects.all().select_related('product').prefetch_related('images')

        out_of_stock_variants = []
        for variant in variants:
            quantity = self.get_variant_quantity(variant)
            if quantity == 0:
                out_of_stock_variants.append(variant)
        
        return out_of_stock_variants
    
    def get_variant_quantity(self, variant):
        total = StockMovement_model.objects.filter(
            product_variant=variant
        ).aggregate(total=Sum('balance'))['total']
        return total if total is not None else 0

class AdminInventorySummaryView(APIView):
    """
    Admin view to get inventory summary statistics.
    """
    permission_classes = [permission_required("inventory.view")]
    
    def get(self, request):
        # Total product variants
        total_variants = ProductVariant.objects.count()
        
        # Total products
        total_products = ProductVariant.objects.values('product').distinct().count()
        
        # Products with stock
        products_with_stock = 0
        total_items = 0
        total_value = 0
        
        variants = ProductVariant.objects.all().select_related('product')
        for variant in variants:
            quantity = self.get_variant_quantity(variant)
            total_items += quantity
            total_value += quantity * float(variant.selling_price) if quantity > 0 else 0
            if quantity > 0:
                products_with_stock += 1
        
        # Low stock count (threshold = 10)
        low_stock_count = 0
        for variant in variants:
            quantity = self.get_variant_quantity(variant)
            if 0 < quantity < 10:
                low_stock_count += 1
        
        # Out of stock count
        out_of_stock_count = 0
        for variant in variants:
            quantity = self.get_variant_quantity(variant)
            if quantity == 0:
                out_of_stock_count += 1
        
        # In stock count (> 50)
        in_stock_count = 0
        for variant in variants:
            quantity = self.get_variant_quantity(variant)
            if quantity > 50:
                in_stock_count += 1
        
        # Medium stock count (10-50)
        medium_stock_count = 0
        for variant in variants:
            quantity = self.get_variant_quantity(variant)
            if 10 <= quantity <= 50:
                medium_stock_count += 1
        
        # Category breakdown
        category_breakdown = {}
        for variant in variants:
            category = variant.product.category.slug if variant.product.category else "uncategorized"
            if category not in category_breakdown:
                category_breakdown[category] = {
                    'count': 0,
                    'items': 0,
                    'value': 0,
                    'out_of_stock': 0,
                    'low_stock': 0,
                    'medium_stock': 0,
                    'in_stock': 0
                }
            quantity = self.get_variant_quantity(variant)
            category_breakdown[category]['count'] += 1
            category_breakdown[category]['items'] += quantity
            category_breakdown[category]['value'] += quantity * float(variant.selling_price)
            
            if quantity <= 0:
                category_breakdown[category]['out_of_stock'] += 1
            elif quantity <= 10:
                category_breakdown[category]['low_stock'] += 1
            elif quantity <= 50:
                category_breakdown[category]['medium_stock'] += 1
            else:
                category_breakdown[category]['in_stock'] += 1
        
        return Response({
            'total_variants': total_variants,
            'total_products': total_products,
            'products_with_stock': products_with_stock,
            'total_items_in_stock': total_items,
            'total_inventory_value': round(total_value, 2),
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'medium_stock_count': medium_stock_count,
            'in_stock_count': in_stock_count,
            'category_breakdown': category_breakdown,
        })
    
    def get_variant_quantity(self, variant):
        total = StockMovement_model.objects.filter(
            product_variant=variant
        ).aggregate(total=Sum('balance'))['total']
        return total if total is not None else 0

class AdminBulkInventoryUpdateView(APIView):
    """
    Admin view to bulk update inventory status.
    """
    permission_classes = [permission_required("products.edit")]
    
    def post(self, request):
        variant_ids = request.data.get('variant_ids', [])
        action = request.data.get('action')  # 'activate' or 'deactivate'
        
        if not variant_ids or not action:
            return Response(
                {'error': 'variant_ids and action are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if action not in ['activate', 'deactivate']:
            return Response(
                {'error': 'action must be "activate" or "deactivate"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        status_bool = action == 'activate'
        updated = ProductVariant.objects.filter(id__in=variant_ids).update(status=status_bool)
        
        return Response({
            'message': f'Successfully updated {updated} variants',
            'updated_count': updated
        })
