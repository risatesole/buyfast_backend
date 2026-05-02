from django.shortcuts import render, redirect
from ....product.services.product.product_service import ProductService

def categories_view(request):
    """
    This view Renders the categories page with store name and all available
    product categories.
    """
    product = ProductService()
    context = {
        "storename": "Petal",
        "categories": product.getAllCategories()
    }
    return render(request, "store/categories/categories_page.html",context)
