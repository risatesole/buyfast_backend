from django.urls import path
from accounts.views.employee_api_view import create_employee
from products.products import products, product_detail ,product_categories, ProductByTagView
from .modules.system.health_api_view import health
from .views import set_product_price
from accounts.accounts import (
    delete_account,                      signup_api_view, 
    signin_api_view,                     signout_api_view, 
    change_password_api_view,            me_api_view)

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
    path('products/',                    products),
    path('productcategories/',           product_categories),
    path('products/<int:product_id>/', product_detail),
    path(
        "products/tag/<str:tag>/",
        ProductByTagView.as_view(),
        name="products-by-tag"
    ),

]
