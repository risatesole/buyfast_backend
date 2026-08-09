# orders/models.py
from django.db import models
from accounts.models import User
from products.default.models import ProductVariant
from payment.models import PaymentProvider, PaymentProviderTransaction


class Order(models.Model):
    class Status(models.TextChoices):
        AWAITING_PAYMENT = "awaiting_payment", "Awaiting Payment"
        PENDING = "pending", "Pending"
        FULFILLED = "fulfilled", "Fulfilled"
        RETURNED = "returned", "Returned"
        CANCELLED = "cancelled", "Cancelled"

    customer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="orders"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AWAITING_PAYMENT
    )
    pickup_time = models.DateTimeField(null=True, blank=True)
    pickup_code = models.CharField(max_length=8, blank=True, default="")
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
        ProductVariant,
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
        return (self.price_per_item + self.tax_amount) * self.quantity


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
    tax_amount = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_payments"

    def __str__(self):
        return f"Payment for Order #{self.order.id} — ${self.amount}"


class OrderCodeView_model(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="code_views"
    )
    viewed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="order_code_views"
    )
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_order_code_view"

    def __str__(self):
        return f"Order #{self.order_id} code viewed by {self.viewed_by.email} at {self.viewed_at}"
