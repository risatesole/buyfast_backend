from ..models.order_model import Order_model

def get_all_orders():
    orders = (
        Order_model.objects
        .select_related("user")
        .prefetch_related("items__product")
        .all()
    )

    result = []

    for order in orders:
        order_data = {
            "id": order.id,
            "user": order.user.email,
            "status": order.status,
            "total_amount": str(order.total_amount),
            "created_at": order.created_at,
            "items": []
        }

        for item in order.items.all(): # type: ignore
            order_data["items"].append({
                "product": str(item.product),
                "quantity": item.quantity,
                "price_at_purchase": str(item.price_at_purchase),
                "subtotal": str(item.get_total())
            })

        result.append(order_data)

    return result
