# from ....models import Category, ProductType, ProductVariant, Product
# # from products.base.models import BaseProduct
# from typing import List, Optional
# from django.utils.text import slugify

# def create_base_product(
#     name: str,
#     description: str,
#     status: bool,
#     selling_price: float,
#     tags: Optional[List[str]],
#     category_slug: str,
#     thumbnail_url: str,
#     sku: str,
#     low_stock_threshold: int
# ) -> Product:
#     category_object = Category.objects.get(slug=category_slug)
#     product_type_object, created = ProductType.objects.get_or_create(
#         name="base",
#         defaults={
#             "name": "base",
#             "description": "basic product",
#             "slug": slugify("base"),
#         }
#     )

#     product_variant_object = ProductVariant.objects.create(
#         slug= slugify(name),
#         price=selling_price,
#         low_stock_threshold=low_stock_threshold,
#         is_active=status,
#     )

#     base_product = BaseProduct.objects.create(
#         product_variant = product_variant_object,
#         name = name,
#         description = description,
#         sku=sku,
#     )

#     product = Product.objects.create(
#         name=name,
#         category=category_object,
#         product_type=product_type_object,
#         status=status,
#         selling_price=selling_price,
#         thumbnail=thumbnail_url,
#         product_variant=product_variant_object,
#     )

#     if tags:
#         product.tags.add(*tags)

#     return product
