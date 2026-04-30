from django.db import models
from .provider_model import Provider
from ...employee.models.employee_model import employee_model

class StockEntry(models.Model):
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="receipts"
    )

    provider = models.ForeignKey(
        Provider,
        on_delete=models.SET_NULL,
        null=True,
        related_name="receipts"
    )

    quantity = models.PositiveIntegerField()
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2) # quantity based in the quantity stablished in the product model

    received_at = models.DateTimeField(auto_now_add=True)

    added_by = models.ForeignKey(
        employee_model,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    note = models.TextField(blank=True, null=True)

    def total_cost(self):
        return self.quantity * self.cost_per_unit
    