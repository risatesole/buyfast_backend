from django.shortcuts import render, get_object_or_404
from ...product.models.model_product import Product
from django.shortcuts import get_object_or_404

def storefront_product_page(request, product_id):
    """View that renders a product detail page by fetching a Product by ID or returning 404 if not found."""
    product = get_object_or_404(Product, id=product_id)
    return render(request, "store/product/product_page.html", {
        "product": product
    })
