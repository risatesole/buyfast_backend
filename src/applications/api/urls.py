from django.urls import path
from .views import health, products, productcategories

urlpatterns = [
    path('health/', health),
    path('products/', products),
    path("productcategories/",productcategories)
]
