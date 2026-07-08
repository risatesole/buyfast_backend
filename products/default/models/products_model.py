from django.db import models
from taggit.managers import TaggableManager
from .category_model import Category
from .product_type_model import ProductType

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

    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
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
    thumbnail = models.CharField(max_length=1000)
    class Meta:
            db_table = "core_product"

    tax_rate = models.DecimalField(
            max_digits=5,
            decimal_places=4,
            default=0.18
        )

    def __str__(self):
        return self.name

