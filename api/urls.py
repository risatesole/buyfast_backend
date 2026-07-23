# api/urls.py
from django.urls import path

# --- System & Root ---
from .views import api_root, set_product_price
from .views_sandbox import ApiSandboxView
from .modules.system.health_api_view import health

# --- Accounts ---
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

# --- Products ---
from products.default.views.products_api_view import ProductDetailView
from products.default.views.product_categories_view import product_categories_api_view
from products.default.views.product_import_csv import ImportProductsCSVView

# --- Cart & Checkout ---
from cart.views.cart_api_view import CartAPIView
from checkout.views.checkout_api_view import (
    checkout_api_view,
    checkout_timeslots_api_view,
)

# --- Orders & Inventory ---
from orders.views.admin.orders_admin_api_view import admin_order_view
from orders.views.admin.order_details_admin_api_view import order_details_admin_view
from orders.views.customers.orders_api_view import OrderDetailView
from inventory.inventory import StockMovementListView

app_name = "api"

urlpatterns = [
    # System & General
    path("", api_root, name="api-root"),
    path("health/", health, name="health"),
    path("test/", ApiSandboxView.as_view(), name="sandbox-test"),

    # Accounts / Auth
    path("me/", me_api_view, name="auth-me"),
    path("signin/", signin_api_view, name="auth-signin"),
    path("signup/", signup_api_view, name="auth-signup"),
    path("signout/", signout_api_view, name="auth-signout"),
    path("change-password/", change_password_api_view, name="auth-change-password"),
    path("delete-account/", delete_account, name="auth-delete-account"),
    path("users/", users, name="admin-users"),
    path("employee/", create_employee, name="admin-create-employee"),

    # Products
    path("products/", ProductDetailView.as_view(), name="product-list"),
    path('products/import/csv/', ImportProductsCSVView.as_view(), name='import_products'),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("products/categories/", product_categories_api_view, name="product-categories"),
    path("products/set-price/", set_product_price, name="product-set-price"),

    # Cart & Checkout
    path("cart/", CartAPIView.as_view(), name="cart-api"),
    path("checkout/", checkout_api_view, name="checkout-api"),
    path("checkout/timeslots/", checkout_timeslots_api_view, name="checkout-timeslots"),

    # Orders
    path("admin/orders/", admin_order_view, name="admin-orders-list"),
    path("admin/orders/<int:pk>/", order_details_admin_view, name="admin-order-detail"),
    path("customers/orders/", OrderDetailView.as_view(), name="customer-orders-list"),
    path("customers/orders/<int:order_id>/", OrderDetailView.as_view(), name="customer-order-detail"),

    # Inventory
    path(
        "admin/inventory/stockmovement/",
        StockMovementListView.as_view(),
        name="admin-stock-movement-list",
    ),
]