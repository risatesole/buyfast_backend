from django.urls import path
from .views_sandbox import ApiSandboxView

from products.default.views.products_api_view import ProductDetailView
from accounts.accounts import (
    change_password_api_view,
    delete_account,
    me_api_view,
    signin_api_view,
    signout_api_view,
    signup_api_view,
)
from accounts.views.admin.users_api_view import users
from accounts.views.employee_api_view import create_employee
from cart.cart import cart_api_view
from checkout.checkout import checkout_api_view, checkout_timeslots_api_view
from inventory.inventory import StockMovementListView
from orders.orders import orders_admin_view , order_details_admin_view

from .modules.system.health_api_view import health
from .views import set_product_price, api_root
from orders.views.customers.orders_api_view import OrderDetailView

from products.default.views.product_categories_view import product_categories_api_view

urlpatterns = [
    path("", api_root, name="api-root"),

    path("test/", ApiSandboxView.as_view(), name="test"),

    path("health/", health, name="health"),
    path("me/", me_api_view, name="me"),
    path("products/set-price/", set_product_price),
    path("signin/", signin_api_view),
    path("signup/", signup_api_view),
    path("signout/", signout_api_view),
    path("change_password/", change_password_api_view),
    path("employee/", create_employee),
    path("delete-account/", delete_account),
    path('products/', ProductDetailView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/categories', product_categories_api_view, name="product-categories"),
    path("cart/", cart_api_view),
    path("checkout/", checkout_api_view),
    path("checkout/timeslots/", checkout_timeslots_api_view),
    path("users/", users),
    path("admin/orders/", orders_admin_view),
    path('admin/orders/<int:pk>/', order_details_admin_view),
    path("customers/orders/",OrderDetailView.as_view(), name="orders-customer-api-view"),
    path("customers/orders/<int:order_id>",OrderDetailView.as_view(),name="orders-api-view"),
    path(
        "admin/inventory/stockmovement",
        StockMovementListView.as_view(),
        name="stock-movement-list",
    ),
]
