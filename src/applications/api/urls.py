from django.urls import path
from .views import health, products, productcategories
from .modules.auth.signup_view import api_signup_view

urlpatterns = [
    path('health/', health),
    path('products/', products),
    path("productcategories/",productcategories),
    path("signup/",api_signup_view),
]
