from ....product.services.product.product_service import ProductService
from django.shortcuts import render

def store_front_context_handler():
    product = ProductService()

    hero_section = {
        "text": {
            "main": "Compra a tu manera",
            "eyebrow": "productos que dicen comprame",
            "supporting": "Descubre cientos de productos seleccionados para cada estilo y ocasión"
        }
    }

    context = {
        "storename": "Petal",
        "hero": hero_section,
        "categories": product.getAllCategories()[:10]

    }
    return context


def storefront_view(request):
    context = store_front_context_handler()
    return render(request, "pages/home/index.html", context)



