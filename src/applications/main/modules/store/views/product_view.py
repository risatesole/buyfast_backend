from django.shortcuts import render, get_object_or_404
from ...product.models.model_product import Product

def storefront_product_page(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    return render(request, "store/product/product_page.html", {
        "product": product
    })



from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from ...product.models.model_product import Product
from ..services.sell_product import sell_product

@login_required
def store_front_buy_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        sell_product(product, request.user)

    return redirect("product_page", product_id=product.id)  # type: ignore
