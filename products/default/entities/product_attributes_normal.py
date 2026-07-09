from dataclasses import dataclass, field
from typing import Optional
from decimal import Decimal
from datetime import datetime

from products.default.value_objects.product_name import ProductName
from products.default.value_objects.product_description import ProductDescription
from products.default.value_objects.product_sku import SKU
from products.default.value_objects.product_slug import Slug
from products.default.value_objects.product_category import ProductCategory
from products.default.value_objects.product_type import ProductType
from products.default.value_objects.product_selling_price import SellingPrice
from products.default.value_objects.product_taxrate import TaxRate
from products.default.value_objects.product_tags import Tags

from products.default.entities.interfaces.product_attributes_interface import ProductAttributes

@dataclass
class ProductAttributesNormal(ProductAttributes):
    """
    A normal product entity with all standard fields.
    This represents a typical product in an e-commerce system.
    """
    name: ProductName
    description: ProductDescription
    SellingPrice: SellingPrice
    tax_rate: TaxRate

    sku: SKU
    slug: Slug

    image_hero: str | None = None
    image_details: str | None = None
    image_thumbnail: str | None = None
    image_gallery: str | None = None
    image_lifestyle: str | None = None

    # Product type is locked to "normal" - hidden from constructor
    product_type: ProductType = field(default_factory=lambda: ProductType("normal"), init=False)

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    id: Optional[int] = None  

    def __post_init__(self):
        pass


if __name__ == "__main__":
    product = ProductAttributesNormal(
        name=ProductName("Apple iPhone 15 Pro"),
        description=ProductDescription(
            "The latest Apple smartphone with an A17 Pro chip and titanium body."
        ),
        SellingPrice=SellingPrice(Decimal("999.99")),
        tax_rate=TaxRate(Decimal("0.18")),
        sku=SKU("IPH15PRO-256-BLK"),
        slug=Slug("apple-iphone-15-pro"),
        image_hero="hero.jpg",
        image_thumbnail="thumb.jpg",
        image_gallery="gallery.jpg",
    )

    print("=== Product ===")
    print(product)

    print("\n=== Individual fields ===")
    print(f"Name: {product.name.value}")
    print(f"Description: {product.description.value}")
    print(f"Price: {product.SellingPrice}")
    print(f"Tax Rate: {product.tax_rate}")
    print(f"SKU: {product.sku}")
    print(f"Slug: {product.slug}")
    print(f"Product Type: {product.product_type}")
    print(f"Hero Image: {product.image_hero}")
    print(f"Thumbnail: {product.image_thumbnail}")
    print(f"Gallery: {product.image_gallery}")
