from ..entities.product_entity import ProductEntity
from ..models import Product, ProductVariant as ProductVariantModel
from ..entities.product_variant import ProductVariant as ProductVariantEntity

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

from ..entities.product_attributes_normal import ProductAttributesNormal

import json
from django.db.models import Q

class ProductRepository:
    def save(self, productentity: ProductEntity):
        name = productentity.name.value
        category = productentity.category.value
        tags = productentity.tags
        thumbnail = productentity.thumbnail
        created_at = productentity.created_at
        updated_at = productentity.updated_at
        product_type = productentity.product_type
        slug = productentity.slug.value

        product_db = Product.objects.create(
            name = name,
            category=category,
            tags = tags,
            thumbnail=thumbnail,
            product_type = product_type,
            slug= slug
        )

        productentity.id = product_db.id

        if productentity.product_type.value == "normal":
            for idx, variant in enumerate(productentity.variants, 1):
                variant_name = variant.attributes.name.value
                variant_description = variant.attributes.description.value
                variant_variantnumber = variant.variantnumber
                variant_sku = variant.attributes.sku.value
                variant_slug = variant.attributes.slug.value
                variant_price = variant.SellingPrice.value
                variant_tax_rate = variant.tax_rate.value

                productvariant_db = ProductVariantModel.objects.create(
                    product=product_db,
                    name=variant_name,
                    description=variant_description,
                    slug=variant_slug,
                    sku=variant_sku,
                    selling_price=variant_price,
                    tax_rate=variant_tax_rate,
                    variantnumber=variant_variantnumber,
                )

                variant.attributes.id = productvariant_db.id
                variant.attributes.name = productvariant_db.name
                variant.attributes.description = productvariant_db.description
                variant.attributes.sku = productvariant_db.sku
                variant.attributes.slug = productvariant_db.slug

                variant.attributes.CreatedAt = productvariant_db.created_at
                variant.attributes.updated_at = productvariant_db.updated_at

        return productentity

    def get_product_by_id(self, product_id: int) -> ProductEntity:
        """
        Retrieve a product by ID and reconstruct it as a ProductEntity with all variants.
        """
        product_db = Product.objects.get(id=product_id)

        product_name = ProductName(product_db.name)
        product_category = ProductCategory(product_db.category)
        product_thumbnail = product_db.thumbnail
        product_slug = Slug(product_db.slug)
        product_tags = list(product_db.tags.values_list('name', flat=True))
        created_at = CreatedAt(product_db.created_at)
        updated_at = UpdatedAt(product_db.updated_at)

        variants_db = ProductVariantModel.objects.filter(product=product_db)

        variants = []
        for variant_db in variants_db:
            # Reconstruct variant-level value objects
            variant_name = ProductName(variant_db.name)
            variant_description = ProductDescription(variant_db.description)
            variant_variantnumber = variant_db.variantnumber
            variant_sku = SKU(variant_db.sku)
            variant_slug = Slug(variant_db.slug)
            variant_price = SellingPrice(variant_db.selling_price)
            variant_tax_rate = TaxRate(variant_db.tax_rate)

            variant_created_at = CreatedAt(variant_db.created_at)
            variant_updated_at = UpdatedAt(variant_db.updated_at)

            # Create ProductAttributesNormal for this variant
            attributes = ProductAttributesNormal(
                id=variant_db.id,
                name=variant_name,
                description=variant_description,
                sku=variant_sku,
                slug=variant_slug,
                image_hero=variant_db.image_hero if hasattr(variant_db, 'image_hero') else None,
                image_thumbnail=variant_db.image_thumbnail if hasattr(variant_db, 'image_thumbnail') else None,
                image_gallery=variant_db.image_gallery if hasattr(variant_db, 'image_gallery') else None,
                created_at=variant_created_at,
                updated_at=variant_updated_at,
            )

            # Create ProductVariantEntity
            variant_entity = ProductVariantEntity(
                id=variant_db.id,
                variantnumber=variant_variantnumber,
                attributes=attributes,
                SellingPrice=variant_price,
                tax_rate=variant_tax_rate
            )
            variants.append(variant_entity)

        # Reconstruct and return the ProductEntity
        # NOTE: Do NOT pass product_type - it's automatically set with init=False
        product_entity = ProductEntity(
            id=product_db.id,
            name=product_name,
            slug=product_slug,
            category=product_category,
            thumbnail=product_thumbnail,
            tags=product_tags,
            variants=variants,
            created_at=created_at,
            updated_at=updated_at
        )

        return product_entity

    def get_product_via_query(self, sort:str=None, status:bool=None, limit:int=None,
                            offset:int=None, tag:str=None, category:str=None,
                            search:str=None):
        """
        get products via query parameters
        """

        filter_params = {}
        q_objects = Q()

        if category:
            filter_params['category'] = category

        if tag:
            # TaggableManager search
            filter_params['tags__name__icontains'] = tag

        if search:
            q_objects |= Q(name__icontains=search)

        # Apply filters
        products = Product.objects.filter(**filter_params)

        if q_objects:
            products = products.filter(q_objects)

        if sort:
            products = products.order_by(sort)

        if limit:
            if offset:
                products = products[offset:offset+limit]
            else:
                products = products[:limit]

        entities = []
        for p in products:
            variant_entities = []
            product_variant_from_model = ProductVariantModel.objects.filter(product=p)

            for variant in product_variant_from_model:
                product_attributes_normal = ProductAttributesNormal(
                    id = variant.id,
                    name= ProductName(variant.name),
                    description= ProductDescription(variant.description),
                    sku= SKU(variant.sku),
                    slug= Slug(variant.slug),
                    # image_hero: str | None = None
                    # image_details: str | None = None
                    # image_thumbnail: str | None = None
                    # image_gallery: str | None = None
                    # image_lifestyle: str | None = None
                    created_at = CreatedAt(variant.created_at),
                    updated_at= UpdatedAt(variant.updated_at)
                )

                product_variant = ProductVariantEntity(
                    variantnumber = variant.variantnumber,
                    attributes=product_attributes_normal,
                    id= variant.id,
                    SellingPrice=SellingPrice(variant.selling_price),
                    tax_rate=TaxRate(variant.tax_rate)
                )
                variant_entities.append(product_variant)

            entity = ProductEntity(
                id=p.id,
                name=ProductName(p.name),
                category=ProductCategory(p.category),
                thumbnail=p.thumbnail,
                slug=Slug(p.slug),
                tags=list(p.tags.values_list('name', flat=True)),
                variants=variant_entities,
                created_at=CreatedAt(p.created_at),
                updated_at=UpdatedAt(p.updated_at),
            )
            entities.append(entity)
        return entities
