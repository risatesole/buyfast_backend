Example usage of the product repository

```py
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

from .product_repository import ProductRepository

from decimal import Decimal

from datetime import datetime, UTC



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
    created_at = CreatedAt(datetime(2025, 1, 15, 10, 30, 0, tzinfo=UTC)),
    updated_at=UpdatedAt(datetime(2025, 1, 15, 10, 30, 0, tzinfo=UTC)),
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
    created_at=CreatedAt(datetime(2025, 1, 15, 10, 30, 0, tzinfo=UTC)),
    updated_at=UpdatedAt(datetime(2025, 1, 15, 10, 30, 0, tzinfo=UTC)),
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
    created_at=CreatedAt(datetime(2025, 1, 15, 10, 30, 0, tzinfo=UTC)),
    updated_at=UpdatedAt(datetime(2025, 1, 15, 10, 30, 0, tzinfo=UTC)),
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
    created_at=CreatedAt(datetime(2025, 1, 15, 10, 30, 0, tzinfo=UTC)),
    updated_at=UpdatedAt(datetime(2025, 1, 15, 10, 30, 0, tzinfo=UTC)),
)

# Save
repository = ProductRepository()
repository.save(productentity=entity)

```


get product entity from the dbms:
```py
# the same imports as the repository files

# Initialize the repository
repository = ProductRepository()

try:
    # Get product with ID 2
    product = repository.get_product_by_id(product_id=2)

    # Print product-level information
    print("=" * 60)
    print("PRODUCT INFORMATION")
    print("=" * 60)
    print(f"Product ID: {product.id}")
    print(f"Product Name: {product.name.value}")
    print(f"Category: {product.category.value}")
    print(f"Product Type: {product.product_type}")
    print(f"Tags: {product.tags}")
    print(f"Created At: {product.created_at.value}")
    print(f"Updated At: {product.updated_at.value}")

    # Print variants information
    print("\n" + "=" * 60)
    print("VARIANTS")
    print("=" * 60)
    print(f"Total Variants: {len(product.variants)}\n")

    for idx, variant in enumerate(product.variants, 1):
        print(f"--- VARIANT {idx} ---")
        print(f"ID: {variant.attributes.id}")
        print(f"Name: {variant.attributes.name.value}")
        print(f"Description: {variant.attributes.description.value}")
        print(f"SKU: {variant.attributes.sku.value}")
        print(f"Slug: {variant.attributes.slug.value}")
        print(f"Selling Price: ${variant.attributes.SellingPrice.value}")
        print(f"Tax Rate: {variant.attributes.tax_rate.value * 100}%")
        print(f"Image Hero: {variant.attributes.image_hero}")
        print(f"Image Thumbnail: {variant.attributes.image_thumbnail}")
        print(f"Image Gallery: {variant.attributes.image_gallery}")
        print(f"Created At: {variant.attributes.created_at.value}")
        print(f"Updated At: {variant.attributes.updated_at.value}")
        print()

    # Additional calculations
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    # Find cheapest variant
    cheapest_variant = min(
        product.variants,
        key=lambda v: float(v.attributes.SellingPrice.value)
    )
    print(f"Cheapest Variant: {cheapest_variant.attributes.name.value}")
    print(f"Price: ${cheapest_variant.attributes.SellingPrice.value}")

    # Find most expensive variant
    most_expensive_variant = max(
        product.variants,
        key=lambda v: float(v.attributes.SellingPrice.value)
    )
    print(f"Most Expensive Variant: {most_expensive_variant.attributes.name.value}")
    print(f"Price: ${most_expensive_variant.attributes.SellingPrice.value}")

    # Calculate average price
    average_price = sum(
        float(v.attributes.SellingPrice.value)
        for v in product.variants
    ) / len(product.variants)
    print(f"Average Price: ${average_price:.2f}")

except Exception as e:
    print(f"Error retrieving product: {type(e).__name__}: {e}")

```
