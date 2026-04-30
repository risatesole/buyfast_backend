from django.db import models
from .provider_model import Provider
from ...employee.models.employee_model import employee_model

class StockPurchase(models.Model):
    provider = models.ForeignKey(
        Provider,
        on_delete=models.SET_NULL,
        null=True
    )
    purchese_price_per_item = models.BooleanField()
    quantity = models.IntegerField()
    reference_doc = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    added_by = models.ForeignKey(
        employee_model,
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return f"Purchase {self.id} - {self.provider} ({self.quantity})"
