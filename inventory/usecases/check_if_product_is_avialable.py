from ..models import StockMovement_model
from products.default.models import ProductVariant

def is_product_available(product_id, required_quantity=1):
    variant = ProductVariant.objects.get(id=product_id)

    latest_movement = (
        variant.stock_movements
        .order_by("-date_time")
        .first()
    )

    if not latest_movement:
        raise Exception(f"product is not avialable")
    
    print(f"[product_is avialable result: {latest_movement.balance >= required_quantity}")

    return latest_movement.balance >= required_quantity
