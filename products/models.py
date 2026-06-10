from django.db import models
from taggit.managers import TaggableManager

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.CharField(max_length=1000, blank=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        db_table = "core_product_category"


class Product(models.Model):
    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("DEACTIVATED", "Deactivated"),
    ]

    METRIC_UNIT_CHOICES = [
        ("UNIT", "Unit"),
        ("PAIR", "Shoe pair"),
        ("BOX", "Box")
    ]

    name = models.CharField(max_length=500)
    description = models.TextField()
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="product"
    )
    status = models.BooleanField(default=True)
    brand = models.CharField(max_length=500)
    metric_unit = models.CharField(
        max_length=10,
        choices=METRIC_UNIT_CHOICES,
        default="UNIT"
    )
    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    tags = TaggableManager(blank=True)
    class Meta:
            db_table = "core_product"

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    IMAGE_TYPES = [
        ("HERO", "Hero"),
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