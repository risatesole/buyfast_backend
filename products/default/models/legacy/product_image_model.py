from django.db import models
from ..products_model import Product

class ProductImage(models.Model):
    IMAGE_TYPES = [
        ("HERO", "Hero"),
        ("ORIGINAL", "Original"),
        ("SCALE", "Scale"),
        ("PACKING", "Packing"),
        ("FLATLAY", "Flatlay"),
        ("FREEZE_FRAME", "Freeze Frame"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.CharField(max_length=1000)

    image_small = models.CharField(max_length=1000)
    image_medium = models.CharField(max_length=1000)
    image_large = models.CharField(max_length=1000)

    image_type = models.CharField(
        max_length=20,
        choices=IMAGE_TYPES
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "image_type"],
                name="unique_image_type_per_product"
            )
        ]

