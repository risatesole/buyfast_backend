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

class ProductRepository:
    def save(self, productentity: ProductEntity):
        name = productentity.name.value
        category = productentity.category.value
        tags = productentity.tags
        created_at = productentity.created_at
        updated_at = productentity.updated_at
        product_type = productentity.product_type

        product_db = Product.objects.create(
            name = name,
            category=category,
            tags = tags,
            thumbnail = "https://example.com",
            product_type = product_type,
        )

        # Handle multiple variants
        for idx, variant in enumerate(productentity.variants, 1):
            variant_name = variant.attributes.name.value
            variant_description = variant.attributes.description.value
            variant_sku = variant.attributes.sku.value
            variant_slug = variant.attributes.slug.value
            variant_price = variant.attributes.SellingPrice.value
            variant_tax_rate = variant.attributes.tax_rate.value

            productvariant_db = ProductVariantModel.objects.create(
                product=product_db,
                name=variant_name,
                description=variant_description,
                slug=variant_slug,
                sku=variant_sku,
                selling_price=variant_price,
                tax_rate=variant_tax_rate,
            )
            variant.attributes.id = productvariant_db.id
            variant.attributes.name = productvariant_db.name
            variant.attributes.description = productvariant_db.description
            variant.attributes.sku = productvariant_db.sku
            variant.attributes.slug = productvariant_db.slug
            variant.attributes.sku = productvariant_db.sku
            variant.attributes.SellingPrice = productvariant_db.selling_price
            variant.attributes.tax_rate = productvariant_db.tax_rate

            variant.attributes.CreatedAt = productvariant_db.created_at
            variant.attributes.updated_at = productvariant_db.updated_at

    def get_product_by_id(self, product_id: int) -> ProductEntity:
        """
        Retrieve a product by ID and reconstruct it as a ProductEntity with all variants.
        """
        product_db = Product.objects.get(id=product_id)

        product_name = ProductName(product_db.name)
        product_category = ProductCategory(product_db.category)
        product_tags = list(product_db.tags.values_list('name', flat=True))
        print(product_tags)
        created_at = CreatedAt(product_db.created_at)
        updated_at = UpdatedAt(product_db.updated_at)

        variants_db = ProductVariantModel.objects.filter(product=product_db)

        variants = []
        for variant_db in variants_db:
            # Reconstruct variant-level value objects
            variant_name = ProductName(variant_db.name)
            variant_description = ProductDescription(variant_db.description)
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
                SellingPrice=variant_price,
                tax_rate=variant_tax_rate,
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
                attributes=attributes
            )
            variants.append(variant_entity)

        # Reconstruct and return the ProductEntity
        # NOTE: Do NOT pass product_type - it's automatically set with init=False
        product_entity = ProductEntity(
            id=product_db.id,
            name=product_name,
            category=product_category,
            tags=product_tags,
            variants=variants,
            created_at=created_at,
            updated_at=updated_at
        )

        return product_entity
