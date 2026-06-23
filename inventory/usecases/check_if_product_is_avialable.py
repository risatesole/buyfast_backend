from ..models import StockMovement_model

def is_product_available(product_id, required_quantity=1):
    latest_movement = (
        StockMovement_model.objects
        .filter(product_id=product_id)
        .order_by("-date_time")
        .first()
    )

    if not latest_movement:
        return False

    return latest_movement.balance >= required_quantity
