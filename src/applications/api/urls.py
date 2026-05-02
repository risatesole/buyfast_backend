from django.urls import path
from .views import health, products, productcategories
from .modules.auth.signup_api_view import signup_api_view

urlpatterns = [
    path('health/', health),
    path('products/', products),
    path("productcategories/",productcategories),
    path("signup/",signup_api_view),
]
