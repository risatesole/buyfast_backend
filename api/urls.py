from django.urls import path

# --- System & Root ---
from .views import api_root, set_product_price
from .views_sandbox import ApiSandboxView
from .modules.system.health_api_view import health

# --- Dashboard ---
from .views_dashboard import admin_dashboard_summary_view

# --- Accounts ---
from accounts.accounts import (
    avatar_upload_api_view,
    change_password_api_view,
    delete_account,
    forgot_password_api_view,
    me_api_view,
    reset_password_api_view,
    signin_api_view,
    signout_api_view,
    signup_api_view,
)
from accounts.views.admin.users_api_view import users, user_details_api_view
from accounts.views.employee_api_view import create_employee

# --- Products ---
from products.default.views.products_api_view import ProductDetailView
from products.default.views.product_categories_view import CategoryView
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
from orders.views.customers.order_voucher_api_view import order_voucher_api_view
from inventory.inventory import StockMovementListView, StockMovementDecreaseView

# --- Inventory Admin Views ---
from inventory.views.admin.inventory_products_admin_view import (
    AdminProductInventoryListView,
    AdminProductInventoryDetailView,
    AdminLowStockView,
    AdminOutOfStockView,
    AdminInventorySummaryView,
    AdminBulkInventoryUpdateView,
)
from inventory.views.admin.reduce_stock_api_view import ReduceStockView

from .views import upload_file_api_view
from store.views import store_carrousel_view


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
    path("forgot-password/", forgot_password_api_view, name="auth-forgot-password"),
    path("reset-password/", reset_password_api_view, name="auth-reset-password"),
    path("delete-account/", delete_account, name="auth-delete-account"),
    path("me/avatar/", avatar_upload_api_view, name="me-avatar-upload"),

    path("users/<int:matricula>/", user_details_api_view, name="admin-user-detail"),
    path("users/", users, name="admin-users"),

    path("employee/", create_employee, name="admin-create-employee"),

    # Products
    path("products/", ProductDetailView.as_view(), name="product-list"),
    path('products/import/csv/', ImportProductsCSVView.as_view(), name='import_products'),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("products/categories/", CategoryView.as_view(), name="product-categories"),
    path("products/categories/<int:pk>/", CategoryView.as_view(), name="product-category-detail"),
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
    path("customers/orders/<int:order_id>/voucher/", order_voucher_api_view, name="customer-order-voucher"),

    # Inventory - Stock Movements
    path('admin/inventory/stockmovement/', StockMovementListView.as_view(), name='stock-movement-list'),
    path('admin/inventory/stockmovement/<int:movement_id>/', StockMovementListView.as_view(), name='stock-movement-detail'),
    path('admin/inventory/stockmovement/decrease/', StockMovementDecreaseView.as_view(), name='stock-movement-decrease'),

    # Inventory - Product Inventory Admin Views
    path('admin/inventory/products/', AdminProductInventoryListView.as_view(), name='admin-inventory-products-list'),
    path('admin/inventory/products/<int:pk>/', AdminProductInventoryDetailView.as_view(), name='admin-inventory-product-detail'),
    path('admin/inventory/low-stock/', AdminLowStockView.as_view(), name='admin-inventory-low-stock'),
    path('admin/inventory/out-of-stock/', AdminOutOfStockView.as_view(), name='admin-inventory-out-of-stock'),
    path('admin/inventory/summary/', AdminInventorySummaryView.as_view(), name='admin-inventory-summary'),
    path('admin/inventory/bulk-update/', AdminBulkInventoryUpdateView.as_view(), name='admin-inventory-bulk-update'),
    path("admin/inventory/stock/reduce/", ReduceStockView.as_view(), name="reduce-stock"),

    path("upload/", upload_file_api_view, name="upload-file"),

    path("ui/carrousel/",store_carrousel_view,name='carrousel-view'),

    # Dashboard
    path("admin/dashboard/summary/", admin_dashboard_summary_view, name="admin-dashboard-summary"),
]
