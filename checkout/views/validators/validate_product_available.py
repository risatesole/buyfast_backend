from inventory.usecases.check_if_product_is_avialable import is_product_available
from products.products import Product_model
from products.models import Product
from inventory.inventory import ProductUnavailableException

def validation_product_avialability(items):
    unavailable_products = []

    for item in items:
        product_id = item["productid"]
        quantity = item["quantity"]

        product = Product.objects.get(id=product_id)

        if not is_product_available(product_id, quantity):
            unavailable_products.append({
                product.name
            })

    # only return error if something is unavailable
    if unavailable_products:
        if unavailable_products:
            raise ProductUnavailableException(unavailable_products)
    return None
