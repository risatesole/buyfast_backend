from django.contrib.auth.decorators import login_required
from ...services.sell_product import sell_product
from django.shortcuts import get_object_or_404, redirect
from ....product.models.model_product import Product

@login_required
def store_front_buy_product(request, product_id):
    """
    View that handles authenticated product purchase by processing 
    POST requests and redirecting to the product page.
    """
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        sell_product(product, request.user)
    return redirect("product_page", product_id=product.id)  # type: ignore
