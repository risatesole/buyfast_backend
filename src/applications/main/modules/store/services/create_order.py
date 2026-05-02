from django.db import transaction
from ..models.order_model import Order_model
from ..models.order_item_model import OrderItem_model


def get_product_price(product):
    price_obj = product.prices.first()
    if not price_obj:
        raise Exception("Product has no price assigned")
    return price_obj.value


def create_order_from_product(product, user):
    """Creates an order for a single product."""

    if user.role != "customer":
        raise Exception("Only customers can place orders")

    price = get_product_price(product)

    with transaction.atomic():

        # ✅ ONLY use valid Order_model fields
        order = Order_model.objects.create(
            user=user,
            total_amount=price,
            status="COMPLETED"
        )

        OrderItem_model.objects.create(
            order=order,
            product=product,
            quantity=1,
            price_at_purchase=price
        )

        return order