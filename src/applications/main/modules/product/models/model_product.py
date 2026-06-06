from django.db import models
from taggit.managers import TaggableManager
from .category_model import Category

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
        related_name="products"
    )
    status = models.BooleanField(default=True)
    brand = models.CharField(max_length=500)
    image = models.CharField(max_length=1000)
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

    def __str__(self):
        return self.name