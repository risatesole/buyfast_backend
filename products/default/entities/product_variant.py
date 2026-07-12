from dataclasses import dataclass, field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from abc import ABC

from products.default.value_objects.product_sku import SKU
from products.default.value_objects.product_slug import Slug
from .interfaces.product_attributes_interface import ProductAttributes

from products.default.value_objects.product_selling_price import SellingPrice
from products.default.value_objects.product_taxrate import TaxRate
from .product_images_entity import ProductImages

@dataclass
class ProductVariant(ABC):
    variantnumber: int
    attributes: ProductAttributes
    sku: SKU
    slug: Slug
    SellingPrice: Optional[SellingPrice] = None
    tax_rate: Optional[TaxRate] = None
    images: Optional[List[ProductImages]] = None  
    id: Optional[int] = None
    thumbnail: Optional[str] = None