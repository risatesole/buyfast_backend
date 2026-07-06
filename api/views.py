from products.default.products import ProductService
from accounts.accounts import AccountRole
from .utils import CsrfExemptSessionAuthentication
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated


from rest_framework.reverse import reverse

@api_view(['GET'])
def api_root(request, format=None):
    """
    ## Welcome to the Backend API Directory

    ### Developer Quick Notes:
    * **Auth Requirement:** Routes like `/me/`, `/products/set-price/`, and `/cart/` require valid session/token authentication.
    * **Format:** Append `?format=json` to any URL if you want raw JSON data instead of this UI.
    """
    return Response({
        "system": {
            "health": reverse("health", request=request, format=format),
        },
        "auth_&_accounts": {
        #     "signin": reverse("signin", request=request, format=format),
        #     "signup": reverse("signup", request=request, format=format),
        #     "signout": reverse("signout", request=request, format=format),
            "current_user_me": reverse("me", request=request, format=format),
        #     "change_password": reverse("change-password", request=request, format=format),
        #     "delete_account": reverse("delete-account", request=request, format=format),
        },
        # "products_&_catalog": {
        #     "all_products": reverse("products-list", request=request, format=format),
        #     "categories": reverse("product-categories", request=request, format=format),
        #     "set_product_price": reverse("set-product-price", request=request, format=format),
        # },
        # "cart_&_checkout": {
        #     "cart": reverse("cart", request=request, format=format),
        #     "checkout": reverse("checkout", request=request, format=format),
        #     "checkout_timeslots": reverse("checkout-timeslots", request=request, format=format),
        # },
        # "admin_&_management": {
        #     "users_list": reverse("users-list", request=request, format=format),
        #     "admin_orders": reverse("admin-orders", request=request, format=format),
        #     "stock_movement": reverse("stock-movement-list", request=request, format=format),
        #     "create_employee": reverse("create-employee", request=request, format=format),
        # }
    })




@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def set_product_price(request):
    user = request.user

    if user.role != AccountRole.EMPLOYEE.value:
        return Response({"status": "error", "message": "Only employees can update product prices"}, status=403)

    service = ProductService()

    product = service.setProductPrice(
        product_id=request.data.get("product_id"),
        selling_price=request.data.get("selling_price")
    )

    if product is None:
        return Response({"status": "error", "message": "Product not found"}, status=404)

    return Response({"status": "ok", "data": product})
