from dataclasses import dataclass, field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

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

from .product_variant import ProductVariant


@dataclass
class ProductEntity:
    """
    A normal product entity with all standard fields.
    This represents a typical product in an e-commerce system.
    """
    name: ProductName
    category: ProductCategory

    tags: Optional[Tags] = None
    variants: List[ProductVariant] = field(default_factory=list)

    created_at: Optional[CreatedAt] = None
    updated_at: Optional[UpdatedAt] = None
    id: Optional[int] = None

    # Product type is locked to "normal" - hidden from constructor
    product_type: ProductType = field(default_factory=lambda: ProductType("normal"), init=False)

    def __post_init__(self):
        pass
