from django.urls import path
from .modules.auth.me_api_view import me_api_view
from .modules.store.buy_product_api_view import buy_product
from .modules.employee.employee_api_view import create_employee
from .views import (
    health,                              products, 
    product_categories,                  set_product_price)

from .modules.auth.auth import (
    delete_account,                      signup_api_view, 
    signin_api_view,                     signout_api_view, 
    change_password_api_view)

urlpatterns = [
    path('health/',                      health),
    path("me/",                          me_api_view),
    path("products/set-price/",          set_product_price),
    path("signin/",                      signin_api_view),
    path("signup/",                      signup_api_view),
    path("signout/",                     signout_api_view ),
    path("change_password/",             change_password_api_view),
    path("employee/",                    create_employee),
    path("delete-account/",              delete_account),
    path("buy-product/",                 buy_product),
    path('products/',                    products),
    path('productcategories/',           product_categories),
]
