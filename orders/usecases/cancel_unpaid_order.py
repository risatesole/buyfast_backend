from ..models import Order
from inventory.inventory import restore_stock


def cancel_unpaid_order(order: Order):
    """
    Restores the stock reserved for an order whose payment failed, was
    declined, or was abandoned, and marks the order as cancelled.

    No-op if the order isn't awaiting payment, so repeated cancel/onError
    callbacks for the same order are safe.
    """
    if order.status != Order.Status.AWAITING_PAYMENT:
        return order

    items = [
        {"productvariantid": item.product_id, "quantity": item.quantity}
        for item in order.items.all()
    ]
    restore_stock(items, f"Order #{order.id} cancelled - payment not completed")

    order.status = Order.Status.CANCELLED
    order.save()
    return order
