from ..entities.product_entity import ProductEntity

class ProductRepository:
    def save(self, productentity: ProductEntity):
        name = productentity.name.value
        category = productentity.category.value
        tags = productentity.tags
        created_at = productentity.created_at
        updated_at = productentity.updated_at

        print(f"product name: {name}")
        print(f"product category: {category}")
        print(f"product tags: {tags}")
        print(f"product created_at: {created_at}")
        print(f"product updated_at: {updated_at}")

        # Handle multiple variants
        for idx, variant in enumerate(productentity.variants, 1):
            print(f"product variant {idx} description: {variant.attributes.description.value}")
            print(f"product variant {idx} SKU: {variant.attributes.sku.value}")
            print(f"product variant {idx} price: {variant.attributes.SellingPrice}")


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
from ..entities.product_variant import ProductVariant
from ..entities.product_entity import ProductEntity

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
variant1 = ProductVariant(id=None,attributes=attributes1)
variant2 = ProductVariant( id=None,attributes=attributes2)
variant3 = ProductVariant( id=None,attributes=attributes3)

# Create entity with all 3 variants
entity = ProductEntity(
    id=1,
    name=name,
    category=category,
    tags=tags,
    variants=[variant1, variant2, variant3],  # List of variants
    created_at=None,
    updated_at=None,
)

# Save
repository = ProductRepository()
repository.save(productentity=entity)
