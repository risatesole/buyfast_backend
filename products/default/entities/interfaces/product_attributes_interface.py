from abc import ABC
from dataclasses import dataclass

from products.default.value_objects.product_selling_price import SellingPrice
from products.default.value_objects.product_taxrate import TaxRate
from products.default.value_objects.product_name import ProductName
from products.default.value_objects.product_description import ProductDescription
from products.default.value_objects.product_sku import SKU
from products.default.value_objects.product_slug import Slug

@dataclass
class ProductAttributes(ABC):
    name: ProductName
    description: ProductDescription
    SellingPrice: SellingPrice
    tax_rate: TaxRate
    sku: SKU
    slug: Slug
