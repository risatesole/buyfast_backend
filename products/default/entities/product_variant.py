from dataclasses import dataclass, field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

from .product_attributes_interface import ProductAttributes

@dataclass
class ProductVariant(ABC):
    attributes:ProductAttributes
