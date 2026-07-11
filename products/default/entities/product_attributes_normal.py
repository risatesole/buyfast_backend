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
from products.default.value_objects.product_tags import Tags
from products.default.value_objects.product_created_at import CreatedAt
from products.default.value_objects.product_updated_at import UpdatedAt

from products.default.entities.interfaces.product_attributes_interface import ProductAttributes

@dataclass
class ProductAttributesNormal(ProductAttributes):
    """
    A normal product entity with all standard fields.
    This represents a typical product in an e-commerce system.
    """
    name: ProductName
    description: ProductDescription
    sku: SKU
    slug: Slug

    image_hero: str | None = None
    image_details: str | None = None
    image_thumbnail: str | None = None
    image_gallery: str | None = None
    image_lifestyle: str | None = None


    created_at: Optional[CreatedAt] = None
    updated_at: Optional[UpdatedAt] = None
    id: Optional[int] = None

    def __post_init__(self):
        pass


if __name__ == "__main__":
    pass
