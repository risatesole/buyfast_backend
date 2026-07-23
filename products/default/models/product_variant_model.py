from .product_model import Product
from django.db import models

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")

    name = models.CharField(max_length=500)  # "Red/Medium", "Hardcover"
    description = models.TextField(blank=True)
    variantnumber = models.IntegerField(null=False, blank=False)
    slug = models.CharField(max_length=500)
    sku = models.CharField(max_length=500, unique=True)
    status = models.BooleanField(
        default=True,
    )

    # Pricing & Tax
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "core_product_variant"
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"
