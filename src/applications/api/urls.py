from django.urls import path
from .modules.auth.me_api_view import me_api_view
from .modules.store.buy_product_api_view import buy_product
from .modules.employee.employee_api_view import create_employee
from .modules.products.products_api_view import products
from .views import (
    health,                               product_categories,                  
    set_product_price,                    product_detail)

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
    path('products/<int:product_id>/', product_detail),
]
