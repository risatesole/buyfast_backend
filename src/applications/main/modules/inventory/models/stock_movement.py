from django.db import models

class StockMovement_model(models.Model):
    MOVEMENT_TYPES = [
        ("initial_inventory", "Initial Inventory"),
        ("purchase_entry", "Purchase Entry"),
        ("customer_sell", "Customer Sell"),
    ]

    date_time = models.DateTimeField()
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    movement_type = models.CharField(
        max_length=50,
        choices=MOVEMENT_TYPES
    )
    document_reference = models.CharField(max_length=255, blank=True)
    quantity = models.IntegerField()
    balance = models.IntegerField()

    def __str__(self):
        return f"{self.product} - {self.movement_type} ({self.quantity})"