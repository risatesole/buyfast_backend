from ..models import StockMovement_model

def is_product_available(product_id, required_quantity=1):
    print(f" executing is avialable function")
    latest_movement = (
        StockMovement_model.objects
        .filter(product_variant_id=product_id)
        .order_by("-date_time")
        .first()
    )

    if not latest_movement:
        raise Exception(f"product is not avialable {latest_movement.product_variant.name}")
    
    print(f"result: {latest_movement.balance >= required_quantity}")
    return latest_movement.balance >= required_quantity
