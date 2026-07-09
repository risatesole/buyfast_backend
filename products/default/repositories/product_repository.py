from ..entities.product_entity import ProductEntity
from ..models import Product, ProductVariant as ProductVariantModel
from ..entities.product_variant import ProductVariant as ProductVariantEntity

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
