from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from ..repositories.product_repository import ProductRepository
from decimal import Decimal
from datetime import datetime, UTC

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
from ..entities.product_entity import ProductEntity
from ..entities.product_variant import ProductVariant
from ..entities.product_attributes_normal import ProductAttributesNormal

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
                            'id': v.id,
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
            try:
                from ..models import Product

                repository = ProductRepository()


                query_param_sort_by = request.GET.get('sort')
                query_param_status = request.GET.get('status')
                query_param_limit = int(request.GET.get('limit'))
                query_param_offset = int(request.GET.get('offset'))
                query_param_tag = request.GET.get('tag')
                query_param_category = request.GET.get('category')
                query_param_search = request.GET.get('search')

                if query_param_status:
                    if query_param_status is "true":
                        query_param_status = True
                    if query_param_status is "false":
                        query_param_status = False
                    if query_param_status is None:
                        query_param_status = None
                        

                repository_products = repository.get_product_via_query(query_param_sort_by,query_param_status,query_param_limit,query_param_offset,query_param_tag,query_param_category,query_param_search)
                
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
        """POST /api/products/ - Create a new product with multiple variants"""

        try:
            # Extract main product data
            product_name = ProductName(str(request.data["data"]["name"]))
            product_category = ProductCategory(request.data["data"]["category"])
            product_tags = Tags(request.data["data"]["tags"]) if request.data["data"].get("tags") else None

            now = datetime.now(UTC)
            created_at = CreatedAt(now)
            updated_at = UpdatedAt(now)

            product_variants = []

            for variant_data in request.data["data"]["variants"]:
                variant_name = ProductName(str(variant_data["name"]))
                variant_description = ProductDescription(str(variant_data["description"]))
                variant_sku = SKU(variant_data["sku"])
                variant_slug = Slug(variant_data["slug"])
                variant_selling_price = SellingPrice(Decimal(variant_data["selling_price"]))
                variant_tax_rate = TaxRate(Decimal(variant_data["tax_rate"]))

                variant_image_hero = variant_data.get("image_hero")
                variant_image_details = variant_data.get("image_details")
                variant_image_thumbnail = variant_data.get("image_thumbnail")
                variant_image_gallery = variant_data.get("image_gallery")
                variant_image_lifestyle = variant_data.get("image_lifestyle")

                product_attributes = ProductAttributesNormal(
                    name=variant_name,
                    description=variant_description,
                    SellingPrice=variant_selling_price,
                    tax_rate=variant_tax_rate,
                    sku=variant_sku,
                    slug=variant_slug,
                    image_hero=variant_image_hero,
                    image_details=variant_image_details,
                    image_thumbnail=variant_image_thumbnail,
                    image_gallery=variant_image_gallery,
                    image_lifestyle=variant_image_lifestyle,
                    created_at=created_at,
                    updated_at=updated_at,
                )

                product_variant = ProductVariant(attributes=product_attributes)

                product_variants.append(product_variant)

            product_entity = ProductEntity(
                name=product_name,
                category=product_category,
                tags=product_tags,
                variants=product_variants,
                created_at=created_at,
                updated_at=updated_at,
            )


            repository = ProductRepository()
            saved_entity = repository.save(productentity=product_entity)

            return Response({
                "message": "Product created successfully",
                "product_id": getattr(saved_entity, 'id', None),
                "variants_count": len(product_variants)
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': f'Error creating product: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def patch(self, request, pk=None):
        """PATCH /api/products/<id>/ - Update a product"""
        return Response({'message': 'Updated'})
