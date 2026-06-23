from django.db import transaction
from ..models import Order, OrderItem, OrderPayment


def create_order(customer, line_items, payment_transaction):
    """
    Creates the order, order items, and order payment atomically.
    If anything fails the entire thing is rolled back.

    customer          — User instance
    line_items        — [{ product_id, name, quantity, unit_price, unit_tax, subtotal }]
    payment_transaction — PaymentProviderTransaction instance
    """

    with transaction.atomic():
        order = Order.objects.create(customer=customer)

        for item in line_items:
            OrderItem.objects.create(
                order=order,
                product_id=item["product_id"],
                quantity=item["quantity"],
                price_per_item=item["unit_price"],
                tax_amount=item["unit_tax"],
            )

        OrderPayment.objects.create(
            order=order,
            payment_provider=payment_transaction.payment_provider,
            payment_provider_transaction=payment_transaction,
            amount=payment_transaction.amount,
            tax_amount=payment_transaction.tax,
        )

    return order
