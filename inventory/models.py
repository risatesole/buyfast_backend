from django.db import models

class StockMovement_model(models.Model):
    MOVEMENT_TYPES = [
        ("initial_inventory", "Initial Inventory"),
        ("purchase_entry", "Purchase Entry"),
        ("customer_sell", "Customer Sell"),
    ]
    date_time = models.DateTimeField(auto_now_add=True)
    product_variant = models.ForeignKey(
        "products.ProductVariant", 
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
