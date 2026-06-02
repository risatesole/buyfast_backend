from django.urls import path
from .views import health, products, product_categories, set_product_price
from .modules.auth.signup_api_view import signup_api_view
from .modules.auth.signin_api_view import signin_api_view
from .modules.auth.signout_api_view import signout_api_view
from .modules.auth.change_password import change_password_api_view
from .modules.auth.me_api_view import me_api_view
from .modules.store.buy_product_api_view import buy_product
from .modules.employee.employee_api_view import create_employee

urlpatterns = [
    path('health/', health),
    path('products/', products),
    path('productcategories/',product_categories),

    path(
        "products/set-price/",
        set_product_price,
        name="set_product_price"
    ),

    path("signin/",signin_api_view),
    path("signup/",signup_api_view),
    path("signout/", signout_api_view ),
    path("change_password/",change_password_api_view),
    path("employee/",create_employee),
    path("buy-product/", buy_product),
    path("me/", me_api_view),
]
