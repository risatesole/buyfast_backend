from django.db import transaction

from ...inventory.models.stock_movement import StockMovement_model


def sell_product(product, user) -> None:
    """
    Sells 1 unit of a product and updates stock movement.
    """

    with transaction.atomic():

        last_movement = (
            StockMovement_model.objects
            .filter(product=product)
            .order_by("-id")
            .first()
        )

        previous_balance = last_movement.balance if last_movement else 0

        quantity_sold = 1
        new_balance = previous_balance - quantity_sold

        StockMovement_model.objects.create(
            product=product,
            movement_type="customer_sell",
            quantity=quantity_sold,
            balance=new_balance,
            document_reference=f"BUY-{product.id}-{user.id}",  # type: ignore
        )

        if new_balance <= 0:
            product.status = "DEACTIVATED"
            product.save()