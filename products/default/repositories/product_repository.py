from ..entities.product_entity import ProductEntity
class ProductRepository:
    def save(self, productentity:ProductEntity):
        print(type(productentity))




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

name = ProductName("apples")
description = ProductDescription("Apple tastes good")
sellingprice = SellingPrice
tax_rate = TaxRate(Decimal("0.10"))

SKU = SKU("12345")
slug = Slug("appleslug")
category = ProductCategory("food")

tags = None


attributes = ProductAttributesNormal(
    name = name,
    description = description,
    SellingPrice = sellingprice,
    tax_rate=tax_rate,
    sku=SKU,
    slug=slug,
    image_hero=None,
    image_details=None,
    image_thumbnail=None,
    image_gallery=None,
    image_lifestyle=None,
    created_at=None,
    updated_at=None,
)


variant = ProductVariant(
    attributes = attributes,
)

entity = ProductEntity(
    name = name,
    category = category,
    tags = tags,
    variants = variant,
    created_at=None,
    updated_at=None,
)

repository = ProductRepository()

repository.save(
    productentity=entity
)
