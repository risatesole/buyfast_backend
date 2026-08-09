from django.db import transaction
from inventory.models import StockMovement_model


def restore_stock(items, reference: str):
    """
    Increases inventory back for each item — the counterpart to sell_products(),
    used when an order's payment fails/is cancelled after stock was reserved.

    items     — [{ productvariantid, quantity }]
    reference — order id or reference string for document_reference
    """

    with transaction.atomic():
        for item in items:
            product_variant_id = item["productvariantid"]
            qty = item["quantity"]

            latest_movement = (
                StockMovement_model.objects
                .filter(product_variant_id=product_variant_id)
                .order_by("-date_time")
                .select_for_update()
                .first()
            )

            new_balance = (latest_movement.balance if latest_movement else 0) + qty

            StockMovement_model.objects.create(
                product_variant_id=product_variant_id,
                movement_type="order_cancelled",
                document_reference=str(reference),
                quantity=qty,
                balance=new_balance,
            )
