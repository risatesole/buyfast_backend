from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from ..repositories.product_repository import ProductRepository
from decimal import Decimal
from datetime import datetime, UTC
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse

from inventory.inventory import create_initial_inventory

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
from ..entities.product_images_entity import ProductImages
from ..entities.product_attributes_normal import ProductAttributesNormal
from ..repositories.product_repository import ProductRepository

from datetime import datetime, timezone

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
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
                            'thumbnail': v.thumbnail,
                            'variantnumber': v.variantnumber,
                            'sku': v.sku.value,
                            'slug': v.slug.value,
                            'selling_price': float(v.SellingPrice.value),
                            'tax_rate': float(v.tax_rate.value),
                            'image_hero': v.attributes.image_hero,
                            'image_thumbnail': v.attributes.image_thumbnail,
                            'image_gallery': v.attributes.image_gallery,
                            'images': [
                                {
                                    'type': img.type,
                                    'url': img.url
                                }
                                for img in (v.images or [])
                            ],
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
                query_param_slug = request.GET.get('slug')
                query_param_variantslug = request.GET.get('variantslug')

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
                product_entity = repository.get_product_via_query(
                                    query_param_sort_by,
                                    query_param_status,
                                    query_param_limit,
                                    query_param_offset,
                                    query_param_tag,
                                    query_param_category,
                                    query_param_search,
                                    slug=query_param_slug,
                                    variantslug=query_param_variantslug,
                                )
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
                                "id": variant.id,
                                "name": variant.attributes.name.value,
                                "description": variant.attributes.description.value,
                                "variantnumber": variant.variantnumber,
                                "thumbnail": variant.thumbnail,
                                "selling_price": float(variant.SellingPrice.value),
                                "tax_rate": float(variant.tax_rate.value),
                                "sku": variant.sku.value,
                                "slug": variant.slug.value,
                                "image_hero":variant.attributes.image_hero,
                                "image_thumbnail": variant.attributes.image_thumbnail,
                                "image_gallery": variant.attributes.image_gallery,
                                "image_lifestyle": variant.attributes.image_lifestyle,
                                "images": [
                                    {
                                        'type': img.type,
                                        'url': img.url
                                    }
                                    for img in (variant.images or [])
                                ]
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
            if not request.user.is_authenticated:
                raise PermissionDenied("Authentication required")

            if not request.user.is_active:
                raise PermissionDenied("Your account is inactive")

            if request.user.role != "employee":  # Use != not is not
                raise PermissionDenied("Only employees are allowed to perform this action")

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
            product_variant_initial_inventory = []

            for variant_data in request.data["data"]["variants"]:
                variant_name = ProductName(str(variant_data["name"]))
                variant_description = ProductDescription(str(variant_data["description"]))
                variant_variantnumber = variant_data["variantnumber"]
                variant_thumbnail = variant_data["thumbnail"]
                variant_sku = SKU(variant_data["sku"])
                variant_slug = Slug(variant_data["slug"])
                variant_selling_price = SellingPrice(Decimal(variant_data["selling_price"]))
                variant_tax_rate = TaxRate(Decimal(variant_data["tax_rate"]))
                
                # get variant initial inventory data to save to the inventory
                variant_initial_inventory = variant_data["initial_inventory"]
                product_variant_initial_inventory.append(
                    {
                        "initialinventory": variant_initial_inventory,
                        "sku": variant_slug
                    }
                )
                variant_image_hero = variant_data.get("image_hero")
                variant_image_details = variant_data.get("image_details")
                variant_image_thumbnail = variant_data.get("image_thumbnail")
                variant_image_gallery = variant_data.get("image_gallery")
                variant_image_lifestyle = variant_data.get("image_lifestyle")

                # Process images array from the request
                variant_images = []
                if variant_data.get("images"):
                    for image_data in variant_data.get("images"):
                        product_image = ProductImages(
                            type=image_data.get("type", "GALLERY"),
                            url=image_data.get("url")
                        )
                        variant_images.append(product_image)

                product_attributes = ProductAttributesNormal(
                    name=variant_name,
                    description=variant_description,
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
                    sku=variant_sku,
                    slug=variant_slug,
                    thumbnail=variant_thumbnail,
                    attributes=product_attributes,
                    SellingPrice=variant_selling_price,
                    tax_rate=variant_tax_rate,
                    images=variant_images if variant_images else None
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

            inventory_by_slug = {
                item["sku"]: item["initialinventory"]
                for item in product_variant_initial_inventory
            }

            for variant in saved_entity.variants:
                quantity = inventory_by_slug[variant.slug]
                create_initial_inventory(
                    variant.id,
                    quantity
                )

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
                            "id": variant.id,
                            "name": variant.attributes.name.value,  # name is ProductName, has .value
                            "description": variant.attributes.description.value,  # description is ProductDescription, has .value
                            "thumbnail": variant.thumbnail,
                            "variantnumber": variant.variantnumber,
                            "sku": variant.sku.value,  # sku is SKU, has .value
                            "slug": variant.slug.value,  # slug is Slug, has .value
                            "selling_price": float(variant.SellingPrice.value),  # SellingPrice, has .value
                            "tax_rate": float(variant.tax_rate.value),  # tax_rate is TaxRate, has .value
                            "images": [
                                {
                                    "type": img.type,
                                    "url": img.url
                                }
                                for img in (variant.images or [])
                            ],
                            # created_at/updated_at are CreatedAt/UpdatedAt objects with .value property
                            "created_at": variant.attributes.created_at.value.isoformat() if variant.attributes.created_at else None,
                            "updated_at": variant.attributes.updated_at.value.isoformat() if variant.attributes.updated_at else None
                        }
                        for variant in saved_entity.variants
                    ]
                },
                "meta":{
                    "variants_count": len(saved_entity.variants),
                    "timestamp": utc_now.isoformat()
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Error creating product: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, pk=None):
        """DELETE /api/products/<id>/ - Delete a product and all its variants"""
        if not pk:
            return Response(
                {'error': 'Product ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Check authentication and permissions
            if not request.user.is_authenticated:
                raise PermissionDenied("Authentication required")

            if not request.user.is_active:
                raise PermissionDenied("Your account is inactive")

            if request.user.role != "employee":
                raise PermissionDenied("Only employees are allowed to perform this action")

            # Delete the product using repository
            repository = ProductRepository()
            deleted = repository.delete_product_by_id(product_id=pk)

            if not deleted:
                return Response(
                    {'error': f'Product with ID {pk} not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                {
                    'message': f'Product {pk} deleted successfully',
                    'id': pk
                },
                status=status.HTTP_200_OK
            )

        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Error deleting product: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def patch(self, request, pk=None):
        """PATCH /api/products/<id>/ - Update a product"""
        return Response({'message': 'Updated'})
