from django.shortcuts import render
from ..context_handlers.category_context_handler import store_category_context_handler

def store_category_view(request, name):
    """
    Renders the category page using context provided by the category 
    context handler.
    """
    context = store_category_context_handler(name)
    return render(request, "store/category/category.html", context)