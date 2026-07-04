from django.urls import path
from .views_sandbox import ApiSandboxView

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
from orders.orders import orders_admin_view
from products.products import (
    ProductByTagView,
    product_categories,
    product_category_detail,
    product_detail,
    products,
)

from .modules.system.health_api_view import health
from .views import set_product_price, api_root

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
    path("products/", products),
    path("products/categories", product_categories),
    path("products/<int:product_id>/", product_detail),
    path("cart/", cart_api_view),
    path("checkout/", checkout_api_view),
    path("checkout/timeslots/", checkout_timeslots_api_view),
    path("users/", users),
    path("admin/orders/", orders_admin_view),
    path("products/tag/<str:tag>/", ProductByTagView.as_view(), name="products-by-tag"),
    path(
        "products/categories/<int:category_id>/",
        product_category_detail,
        name="product-category-detail",
    ),
    path(
        "admin/inventory/stockmovement",
        StockMovementListView.as_view(),
        name="stock-movement-list",
    ),
]
