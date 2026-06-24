from ..models import StockMovement_model

def create_initial_inventory(product, quantity):
    """
    Creates the initial inventory record for a product.
    """

    StockMovement_model.objects.create(
        product=product,
        movement_type="initial_inventory",
        quantity=quantity,
        balance=quantity,
    )
