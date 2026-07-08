from django.db import models
from taggit.managers import TaggableManager
from .category_model import Category
from .product_type_model import ProductType
from .product_variant_model import ProductVariant

class Product(models.Model):
    name = models.CharField(max_length=500)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="product"
    )

    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )

    status = models.BooleanField(default=True)
    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    tags = TaggableManager(blank=True)
    thumbnail = models.CharField(max_length=1000)

    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="products"
    )

    class Meta:
            db_table = "core_product"

    def __str__(self):
        return self.name
