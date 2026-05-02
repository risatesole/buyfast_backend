from django.db import models
from ...product.models.model_product import Product
from .order_model import Order_model


class OrderItem_model(models.Model):
    order = models.ForeignKey(
        Order_model,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)

    price_at_purchase = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def get_total(self):
        """Returns total price for this item."""
        return self.quantity * self.price_at_purchase

    def __str__(self):
        return f"Order {self.order.id} - {self.product} x{self.quantity}" # type: ignore