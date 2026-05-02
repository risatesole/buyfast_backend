from django.urls import path
from .views import health, products

urlpatterns = [
    path('health/', health),
    path('products/', products)
]
