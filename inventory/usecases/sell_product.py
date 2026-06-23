from django.db import transaction
from inventory.models import StockMovement_model
from inventory.inventory import ProductUnavailableException


def sell_products(items, order_reference: str):
    """
    Decreases inventory for each item in the order.
    Raises ProductUnavailableException if any product has insufficient stock.
    All movements are created atomically — if one fails, none are recorded.

    items         — [{ product_id, quantity }]
    order_reference — order id or reference string for document_reference
    """

    with transaction.atomic():
        for item in items:
            product_id = item["product_id"]
            qty        = item["quantity"]

            latest_movement = (
                StockMovement_model.objects
                .filter(product_id=product_id)
                .order_by("-date_time")
                .select_for_update()  # ← locks the row to prevent race conditions
                .first()
            )

            if not latest_movement or latest_movement.balance < qty:
                raise ProductUnavailableException([product_id])

            new_balance = latest_movement.balance - qty

            StockMovement_model.objects.create(
                product_id=product_id,
                movement_type="customer_sell",
                document_reference=str(order_reference),
                quantity=qty,
                balance=new_balance,
            )
