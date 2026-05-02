from django.shortcuts import render
from django.http import Http404
from ...product.models.model_product import Product

def store_category_view(request, name):
    category_key = name.upper()

    valid_categories = [c[0] for c in Product.CATEGORY_CHOICE]

    if category_key not in valid_categories:
        raise Http404("Category not found")

    products = Product.objects.filter(
        category=category_key,
        status="ACTIVE"
    )

    context = {
        "category": category_key,
        "products": products
    }

    return render(request, "store/category/category.html", context)
