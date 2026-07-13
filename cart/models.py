from django.conf import settings
from django.db import models
from products.default.models import ProductVariant


class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )

    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )

    quantity = models.PositiveIntegerField(default=1)

    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # unique_together = ("user", "product")
        pass

    def __str__(self):
        return f"{self.user} - {self.product} ({self.quantity})"
