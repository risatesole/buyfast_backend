from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from ..repositories.product_repository import ProductRepository
from decimal import Decimal

from ..value_objects.product_name import ProductName
from ..value_objects.product_description import ProductDescription
from ..value_objects.product_sku import SKU
from ..value_objects.product_slug import Slug
from ..value_objects.product_category import ProductCategory
from ..value_objects.product_type import ProductType
from ..value_objects.product_selling_price import SellingPrice
from ..value_objects.product_taxrate import TaxRate
from ..value_objects.product_tags import Tags
from ..value_objects.product_created_at import CreatedAt
from ..value_objects.product_updated_at import UpdatedAt


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

        # Extract main product data
        product_name = ProductName(str(request.data["data"]["name"]))
        product_category = ProductCategory(request.data["data"]["category"])
        product_tags = Tags(request.data["data"]["tags"])

        # Extract all variant fields for processing
        for variant in request.data["data"]["variants"]:
            variant_name = ProductName(str(variant["name"]))

            variant_description = ProductDescription(str(variant["description"]))
            variant_sku = SKU(variant["sku"])
            variant_slug = Slug(variant["slug"])
            variant_selling_price = SellingPrice(Decimal(variant["selling_price"]))
            variant_tax_rate = TaxRate(Decimal(variant["tax_rate"]))
            variant_image_hero = variant["image_hero"]
            variant_image_thumb = variant["image_thumbnail"]
            variant_image_gallery = variant["image_gallery"]


        return Response({
            "message": "got it"
        }, status=status.HTTP_201_CREATED)

    def patch(self, request, pk=None):
        """PATCH /api/products/<id>/ - Update a product"""
        return Response({'message': 'Updated'})
