from ..context_handlers.storefront_context_handler import store_front_context_handler
from django.shortcuts import render

def storefront_view(request):
    context = store_front_context_handler()
    return render(request, "pages/home/index.html", context)
