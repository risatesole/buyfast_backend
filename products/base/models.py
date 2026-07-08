from django.db import models
from products.default.models import ProductVariant

class BaseProduct(models.Model):
    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="baseproduct",
    )
    name = models.CharField(max_length=500)
    description = models.CharField(max_length=500)
    sku = models.CharField(max_length=500)
    class Meta:
        db_table = "productbase"
    def __str__(self):
        return self.title

class ProductImage(models.Model):
    IMAGE_TYPE_CHOICES = [
        ('HERO', 'Hero'),
        ('PACKAGE', 'Package'),
        ('LIFESTYLE', 'Lifestyle'),
        ('DETAIL', 'Detail'),
    ]

    base_product = models.ForeignKey(
        BaseProduct,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField()
    image_type = models.CharField(
        max_length=20,
        choices=IMAGE_TYPE_CHOICES
    )
    alt_text = models.CharField(
        max_length=500,
        blank=True
    )

    class Meta:
        db_table = "product_base_image"
        ordering = ["image_type"]
    def __str__(self):
        return f"{self.base_product.sku} - {self.image_type}"
