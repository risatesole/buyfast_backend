from django.db import models
from accounts.models import User
from products.models import Product
from payment.models import PaymentProvider, PaymentProviderTransaction


class Order(models.Model):
    customer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="orders"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order"

    def __str__(self):
        return f"Order #{self.id} — {self.customer.email}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items"
    )
    quantity = models.IntegerField()
    price_per_item = models.FloatField()
    tax_amount = models.FloatField(default=0)

    class Meta:
        db_table = "order_items"

    def __str__(self):
        return f"{self.product.name} x{self.quantity} — Order #{self.order.id}"

    @property
    def subtotal(self):
        return (self.price_per_item + self.taxamount) * self.quantity


class OrderPayment(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.PROTECT,
        related_name="payment"
    )
    payment_provider = models.ForeignKey(
        PaymentProvider,
        on_delete=models.PROTECT,
        related_name="order_payments"
    )
    payment_provider_transaction = models.ForeignKey(
        PaymentProviderTransaction,
        on_delete=models.PROTECT,
        related_name="order_payments"
    )
    amount = models.FloatField()
    tax_amount  = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_payments"

    def __str__(self):
        return f"Payment for Order #{self.order.id} — ${self.amount}"

