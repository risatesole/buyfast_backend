from django.db import models
from accounts.models import User
from products.default.models import ProductVariant

class StockMovement_model(models.Model):
    MOVEMENT_TYPES = [
        ("initial_inventory", "Initial Inventory"),
        ("purchase_entry", "Purchase Entry"),
        ("customer_sell", "Customer Sell"),
        ("manual_decrease", "Manual Decrease"),
    ]
    date_time = models.DateTimeField(auto_now_add=True)
    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="stock_movements"
    )
    movement_type = models.CharField(
        max_length=50,
        choices=MOVEMENT_TYPES
    )
    document_reference = models.CharField(max_length=255, blank=True)
    quantity = models.IntegerField()
    balance = models.IntegerField()
    
    class Meta:
        db_table = "core_stock_movement"

    def __str__(self):
        return f"{self.product_variant} - {self.movement_type} ({self.quantity})"


class StockDecrease_model(models.Model):
    """
    Records who decreased inventory and why, alongside the StockMovement_model
    row that actually carries the quantity/balance change.
    """
    stock_movement = models.OneToOneField(
        StockMovement_model,
        on_delete=models.CASCADE,
        related_name="stock_decrease"
    )
    decreased_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="stock_decreases"
    )
    reason = models.CharField(max_length=255)
    date_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_stock_decrease"

    def __str__(self):
        return f"{self.stock_movement} - {self.decreased_by} - {self.reason}"


class StockEntry_model(models.Model):
    """
    Records who registered a stock entry and their stated reason, alongside
    the StockMovement_model row that actually carries the quantity/balance
    change.
    """
    stock_movement = models.OneToOneField(
        StockMovement_model,
        on_delete=models.CASCADE,
        related_name="stock_entry"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="stock_entries"
    )
    reason = models.CharField(max_length=255, blank=True)
    date_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_stock_entry"

    def __str__(self):
        return f"{self.stock_movement} - {self.created_by} - {self.reason}"
