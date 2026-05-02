from django.shortcuts import render, get_object_or_404
from ...product.models.model_product import Product

def storefront_product_page(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    return render(request, "store/product/product_page.html", {
        "product": product
    })