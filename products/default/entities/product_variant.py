from dataclasses import dataclass, field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from abc import ABC

from .interfaces.product_attributes_interface import ProductAttributes

from products.default.value_objects.product_selling_price import SellingPrice
from products.default.value_objects.product_taxrate import TaxRate

@dataclass
class ProductVariant(ABC):
    attributes: ProductAttributes
    SellingPrice: Optional[SellingPrice] = None
    tax_rate: Optional[TaxRate] = None
    id: Optional[int] = None