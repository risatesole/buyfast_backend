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
from ..repositories.product_repository import ProductRepository

from datetime import datetime, timezone

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
                    'thumbnail': product_entity.thumbnail,
                    'slug': product_entity.slug.value,
                    'product_type': product_entity.product_type.value,
                    'tags': product_entity.tags,  # Now it's a list, not TaggableManager
                    'created_at': product_entity.created_at.value.isoformat(),
                    'updated_at': product_entity.updated_at.value.isoformat(),
                    'variants': [
                        {
                            'id': v.id,
                            'name': v.attributes.name.value,
                            'description': v.attributes.description.value,
                            'variantnumber': v.variantnumber,
                            'sku': v.attributes.sku.value,
                            'slug': v.attributes.slug.value,
                            'selling_price': float(v.SellingPrice.value),
                            'tax_rate': float(v.tax_rate.value),
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
                query_param_sort_by = request.GET.get('sort')
                query_param_status = request.GET.get('status')
                query_param_offset = int(request.GET.get('offset', '0'))
                query_param_tag = request.GET.get('tag')
                query_param_category = request.GET.get('category')
                query_param_search = request.GET.get('search')
                query_param_limit = request.GET.get('limit')

                if query_param_status:
                    if query_param_status is "true":
                        query_param_status = True
                    if query_param_status is "false":
                        query_param_status = False
                    if query_param_status is None:
                        query_param_status = None


                if query_param_limit is None:
                    query_param_limit = 100
                else:
                    query_param_limit = int(query_param_limit)

                repository = ProductRepository()
                product_entity = repository.get_product_via_query(query_param_sort_by,query_param_status,query_param_limit,query_param_offset,query_param_tag,query_param_category,query_param_search)
                utc_now = datetime.now(timezone.utc)
                products_data = {
                    "data":[
                        {
                        'id': product_entity.id,
                        'name': product_entity.name.value,
                        'category': product_entity.category.value,
                        'product_type': product_entity.product_type.value,
                        'thumbnail': product_entity.thumbnail,
                        'slug': product_entity.slug.value,
                        "type": product_entity.product_type.value,
                        # 'tags': product_entity.tags if product_entity.tags else None, # TODO: return the tags
                        "variants":[
                            {
                                "name": variant.attributes.name.value,
                                "description": variant.attributes.description.value,
                                "variantnumber": variant.variantnumber,
                                "selling_price": float(variant.SellingPrice.value),
                                "tax_rate": float(variant.tax_rate.value),
                                "sku": variant.attributes.sku.value,
                                "slug": variant.attributes.slug.value,
                                "image_hero":variant.attributes.image_hero,
                                "image_thumbnail": variant.attributes.image_thumbnail,
                                "image_gallery": variant.attributes.image_gallery,
                                "image_lifestyle": variant.attributes.image_lifestyle
                            }
                            for variant in product_entity.variants
                        ]
                        }
                        for product_entity in product_entity
                    ],
                    "meta":{
                        "timestamp": utc_now
                    }
                    }

                return Response(products_data, status=status.HTTP_200_OK)

            except Exception as e:
                print(f"{request.GET.get('limit')}")
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
            product_slug = Slug(request.data["data"]["slug"])
            product_tags = Tags(request.data["data"]["tags"]) if request.data["data"].get("tags") else None
            product_thumbnail = request.data["data"]["thumbnail"]

            now = datetime.now(UTC)
            created_at = CreatedAt(now)
            updated_at = UpdatedAt(now)

            product_variants = []

            for variant_data in request.data["data"]["variants"]:
                variant_name = ProductName(str(variant_data["name"]))
                variant_description = ProductDescription(str(variant_data["description"]))
                variant_variantnumber = variant_data["variantnumber"]
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

                product_variant = ProductVariant(
                    variantnumber=variant_variantnumber,
                    attributes=product_attributes,
                    SellingPrice=variant_selling_price,
                    tax_rate=variant_tax_rate
                )

                product_variants.append(product_variant)

            product_entity = ProductEntity(
                name=product_name,
                category=product_category,
                thumbnail=product_thumbnail,
                slug=product_slug,
                tags=product_tags,
                variants=product_variants,
                created_at=created_at,
                updated_at=updated_at,
            )


            repository = ProductRepository()
            saved_entity = repository.save(productentity=product_entity)

            utc_now = datetime.now(timezone.utc)

            return Response({
            "message": "Product created successfully",
            "data": {
                "id": saved_entity.id,
                "name": saved_entity.name.value,
                "category": saved_entity.category.value,
                'product_type': saved_entity.product_type.value,
                "thumbnail": saved_entity.thumbnail,
                "slug": saved_entity.slug.value,
                "tags": saved_entity.tags.value if saved_entity.tags else None,
                "variants": [
                    {
                        "id": variant.attributes.id,
                        "name": variant.attributes.name,
                        "description": variant.attributes.description,
                        "variantnumber": variant.variantnumber,
                        "sku": variant.attributes.sku,
                        "slug": variant.attributes.slug,
                        "selling_price": float(variant.SellingPrice.value),
                        "tax_rate": float(variant.tax_rate.value),
                        "created_at": variant.attributes.created_at.value,
                        "updated_at": variant.attributes.updated_at
                    }
                    for variant in saved_entity.variants
                ]
            },
            "meta":{
                "variants_count": len(saved_entity.variants),
                "timestamp": utc_now
            }
        }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': f'Error creating product: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def patch(self, request, pk=None):
        """PATCH /api/products/<id>/ - Update a product"""
        return Response({'message': 'Updated'})
