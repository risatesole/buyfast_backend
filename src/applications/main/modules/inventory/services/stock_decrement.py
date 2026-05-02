from django.db import transaction
from ..models.stock_movement import StockMovement_model

def stock_decrement(product, quantity, reference=None):
    """Decreases product stock and records a STORE_DECREMENT movement."""

    with transaction.atomic():
        last_movement = (
            StockMovement_model.objects
            .filter(product=product)
            .order_by("-id")
            .first()
        )

        previous_balance = last_movement.balance if last_movement else 0
        new_balance = previous_balance - quantity

        StockMovement_model.objects.create(
            product=product,
            movement_type="STORE_DECREMENT",
            quantity=quantity,
            balance=new_balance,
            document_reference=reference,
        )

        if new_balance <= 0:
            product.status = "DEACTIVATED"
            product.save()
