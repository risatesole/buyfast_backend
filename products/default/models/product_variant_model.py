from django.db import models

class ProductVariant(models.Model):
    """
    Represents a specific variant of a product (e.g., Red/Medium T-shirt).
    Each variant has its own SKU, price, and stock.
    """
    # Unique identifier for this specific variant
    sku = models.CharField(
        max_length=100,
        unique=True,
        db_index=True
    )

    # Pricing - overrides parent product price if set
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Override price for this variant. If null, use parent product price."
    )

    # Inventory
    stock_quantity = models.PositiveIntegerField(
        default=0
    )

    low_stock_threshold = models.PositiveIntegerField(
        default=5,
        help_text="Alert when stock falls below this number"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive variants won't be shown to customers"
    )

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_product_variant"
        verbose_name = "Product Variant"
        verbose_name_plural = "Product Variants"
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["stock_quantity"]),
        ]

    def __str__(self):
        variant_name = f"{self.product.name}"
        if self.color:
            variant_name += f" - {self.color}"
        if self.size:
            variant_name += f" ({self.size})"
        return variant_name

    @property
    def effective_price(self):
        """Returns variant price or falls back to parent product price"""
        return self.price or self.product.selling_price

    @property
    def is_in_stock(self):
        """Returns True if stock is available"""
        return self.stock_quantity > 0

    @property
    def is_low_stock(self):
        """Returns True if stock is below threshold"""
        return self.stock_quantity <= self.low_stock_threshold

    def reduce_stock(self, quantity=1):
        """Reduces stock quantity, returns True if successful"""
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            self.save(update_fields=["stock_quantity"])
            return True
        return False

    def increase_stock(self, quantity=1):
        """Increases stock quantity"""
        self.stock_quantity += quantity
        self.save(update_fields=["stock_quantity"])
