
from django.shortcuts import render

def store_category_view(request, name):
    return render(request, "store/category/category.html")
