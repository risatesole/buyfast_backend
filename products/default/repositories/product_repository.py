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

        print(f"db name = {product_db.name}")

        print(f"product name: {name}")
        print(f"product category: {category}")
        print(f"product tags: {tags}")
        print(f"product created_at: {created_at}")
        print(f"product updated_at: {updated_at}")
        print(f"product type:{product_type}")

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

            print(f"{productvariant_db.slug}")
            print(f"product variant name: {productvariant_db.name}")
            print(f"product variant description: {productvariant_db.description}")
            print(f"product variant slug: {productvariant_db.slug}")
            print(f"product variant sku: {productvariant_db.sku}")
            print(f"product variant sku: {productvariant_db.sku}")
            print(f"product variant selling_price: {productvariant_db.selling_price}")
            print(f"product variant tax_rate: {productvariant_db.tax_rate}")




# debug:
from ..value_objects.product_name import ProductName
from ..value_objects.product_description import ProductDescription
from ..value_objects.product_sku import SKU
from ..value_objects.product_slug import Slug
from ..value_objects.product_category import ProductCategory
from ..value_objects.product_type import ProductType
from ..value_objects.product_selling_price import SellingPrice
from ..value_objects.product_taxrate import TaxRate
from ..value_objects.product_tags import Tags

from ..entities.product_attributes_normal import ProductAttributesNormal

from decimal import Decimal

# Create base product info
name = ProductName("Apples")
category = ProductCategory("food")
tags = None

# Create 3 variants with different attributes
# Variant 1 - Small Apples
attributes1 = ProductAttributesNormal(
    id=None,
    name=ProductName("Small Apples"),
    description=ProductDescription("Small fresh apples, perfect for snacking"),
    SellingPrice=SellingPrice(Decimal("2.99")),
    tax_rate=TaxRate(Decimal("0.10")),
    sku=SKU("APPLE-SMALL-001"),
    slug=Slug("small-apples"),
    image_hero="small-apples-hero.jpg",
    image_thumbnail="small-apples-thumb.jpg",
    image_gallery="small-apples-gallery.jpg",
    created_at=None,
    updated_at=None,
)

# Variant 2 - Medium Apples
attributes2 = ProductAttributesNormal(
    id=None,
    name=ProductName("Medium Apples"),
    description=ProductDescription("Medium-sized fresh apples, great for baking"),
    SellingPrice=SellingPrice(Decimal("3.99")),
    tax_rate=TaxRate(Decimal("0.10")),
    sku=SKU("APPLE-MEDIUM-002"),
    slug=Slug("medium-apples"),
    image_hero="medium-apples-hero.jpg",
    image_thumbnail="medium-apples-thumb.jpg",
    image_gallery="medium-apples-gallery.jpg",
    created_at=None,
    updated_at=None,
)

# Variant 3 - Large Apples
attributes3 = ProductAttributesNormal(
    id=None,
    name=ProductName("Large Apples"),
    description=ProductDescription("Large fresh apples, perfect for pies and cooking"),
    SellingPrice=SellingPrice(Decimal("4.99")),
    tax_rate=TaxRate(Decimal("0.10")),
    sku=SKU("APPLE-LARGE-003"),
    slug=Slug("large-apples"),
    image_hero="large-apples-hero.jpg",
    image_thumbnail="large-apples-thumb.jpg",
    image_gallery="large-apples-gallery.jpg",
    created_at=None,
    updated_at=None,
)

# Create variant objects
variant1 = ProductVariantEntity(id=None, attributes=attributes1)
variant2 = ProductVariantEntity(id=None, attributes=attributes2)
variant3 = ProductVariantEntity(id=None, attributes=attributes3)

# Create entity with all 3 variants
entity = ProductEntity(
    id=1,
    name=name,
    category=category,
    tags=tags,
    variants=[variant1, variant2, variant3],
    created_at=None,
    updated_at=None,
)

# Save
repository = ProductRepository()
repository.save(productentity=entity)
