from inventory.usecases.check_if_product_is_avialable import is_product_available
from products.default.models import ProductVariant
from inventory.inventory import ProductUnavailableException

def validation_product_avialability(items):
    """
    Validate that all product variants in items are available.
    
    Expects items with: productvariantid, quantity
    """
    unavailable_products = []

    for item in items:
        product_variant_id = item["productvariantid"]
        quantity = item["quantity"]

        product_variant = ProductVariant.objects.get(id=product_variant_id)

        if not is_product_available(product_variant_id, quantity):
            unavailable_products.append({
                product_variant.name
            })

    # only return error if something is unavailable
    if unavailable_products:
        if unavailable_products:
            raise ProductUnavailableException(unavailable_products)
    return None