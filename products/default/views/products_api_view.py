from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from ..repositories.product_repository import ProductRepository


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk=None):
        """GET /api/products/<id>/ - Get a specific product with all variants"""
        if pk:
            try:
                # Get product from repository
                repository = ProductRepository()
                product_entity = repository.get_product_by_id(product_id=pk)

                # Build simple JSON response
                response_data = {
                    'id': product_entity.id,
                    'name': product_entity.name.value,
                    'category': product_entity.category.value,
                    'product_type': product_entity.product_type.value,
                    'tags': product_entity.tags,  # Now it's a list, not TaggableManager
                    'created_at': product_entity.created_at.value.isoformat(),
                    'updated_at': product_entity.updated_at.value.isoformat(),
                    'variants': [
                        {
                            'id': v.attributes.id,
                            'name': v.attributes.name.value,
                            'description': v.attributes.description.value,
                            'sku': v.attributes.sku.value,
                            'slug': v.attributes.slug.value,
                            'selling_price': float(v.attributes.SellingPrice.value),
                            'tax_rate': float(v.attributes.tax_rate.value),
                            'image_hero': v.attributes.image_hero,
                            'image_thumbnail': v.attributes.image_thumbnail,
                            'image_gallery': v.attributes.image_gallery,
                            'created_at': v.attributes.created_at.value.isoformat(),
                            'updated_at': v.attributes.updated_at.value.isoformat(),
                        }
                        for v in product_entity.variants
                    ]
                }
                return Response(response_data, status=status.HTTP_200_OK)

            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_404_NOT_FOUND
                )

        else:
            # GET /api/products/ - List all products
            try:
                from ..models import Product
                products = Product.objects.all()

                products_data = [
                    {
                        'id': p.id,
                        'name': p.name,
                        'category': p.category,
                        'thumbnail': p.thumbnail,
                        'created_at': p.created_at.isoformat() if p.created_at else None,
                    }
                    for p in products
                ]

                return Response(products_data, status=status.HTTP_200_OK)

            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

    def post(self, request, pk=None):
        """POST /api/products/ - Create a new product"""
        return Response({'message': 'Created'}, status=status.HTTP_201_CREATED)

    def patch(self, request, pk=None):
        """PATCH /api/products/<id>/ - Update a product"""
        return Response({'message': 'Updated'})
