from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from ...services.sell_product import sell_product
from ....product.models.model_product import Product

@login_required
def store_front_buy_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        try:
            sell_product(product, request.user)
            messages.success(request, "Product purchased successfully.")
        except Exception as e: 
            messages.error(request, str(e))

    return redirect("product_page", product_id=product.id) # type: ignore