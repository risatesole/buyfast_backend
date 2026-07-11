from abc import ABC
from dataclasses import dataclass
from typing import Optional

from products.default.value_objects.product_name import ProductName
from products.default.value_objects.product_description import ProductDescription
from products.default.value_objects.product_sku import SKU
from products.default.value_objects.product_slug import Slug

@dataclass
class ProductAttributes(ABC):
    name: ProductName
    description: ProductDescription
    sku: SKU
    slug: Slug
    id: Optional[int] = None
