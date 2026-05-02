from django.db import transaction
from ..models.order_model import Order_model
from ..models.order_item_model import OrderItem_model

def create_order_from_product(product, user):
    """Creates an order for a single product, records the item, and updates inventory."""

    if user.role != "customer":
        raise Exception("Only customers can place orders")

    with transaction.atomic():
        # 1. Create order
        order = Order_model.objects.create(
            user=user,
            total_amount=product.price,
            status="COMPLETED" # warning: this is asuming the order is completed uppon user hitting buy, change this to pending 
        )

        OrderItem_model.objects.create(
            order=order,
            product=product,
            quantity=1,
            price_at_purchase=product.price
        )
        return order
