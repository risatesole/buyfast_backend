from django.shortcuts import render, redirect
from .modules.product.services.product.product_service import ProductService

def categories_view(request):
    product = ProductService()
    context = {
        "storename": "Petal",
        "categories": product.getAllCategories()
    }
    return render(request, "store/categories/categories_page.html",context)


