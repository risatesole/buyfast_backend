from ..models import StockMovement_model
from products.default.models import ProductVariant

def create_initial_inventory(product_variant_id, quantity):
    """
    Creates the initial inventory record for a product.
    """    
    product_variant = ProductVariant.objects.get(id=product_variant_id)
    
    StockMovement_model.objects.create(
        product_variant=product_variant,
        movement_type="initial_inventory",
        quantity=quantity,
        balance=quantity,
        document_reference = f"Initial inventory sir. todo create document of reference based in user credentials"
    )
