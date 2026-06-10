from products.products import ProductService
from products.products import CategoryService
from accounts.accounts import AccountRole
from .utils import CsrfExemptSessionAuthentication
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

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


@api_view(['GET', 'POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
def product_categories(request):
    service = CategoryService()

    if request.method == 'GET':
        status = request.query_params.get("status")
        if status == "true":
            status = True
        elif status == "false":
            status = False
        else:
            status = None
        return Response({"status": "ok", "data": service.getCategories(status=status)})

    user = request.user
    if not user.is_authenticated:
        return Response({"status": "error", "message": "Authentication required"}, status=401)
    if user.role != AccountRole.EMPLOYEE.value:
        return Response({"status": "error", "message": "Only employees can create categories"}, status=403)

    category = service.setCategory(
        name=request.data.get("name"),
        slug=request.data.get("slug"),
        description=request.data.get("description", ""),
        image=request.data.get("image", ""),
        status=request.data.get("status", True),
    )
    return Response({"status": "created", "data": category}, status=201)


from .modules.products.handlers.products_patch_handler import products_patch_handler

@api_view(['GET', 'PATCH'])
@authentication_classes([CsrfExemptSessionAuthentication])
def product_detail(request, product_id):
    if request.method == 'GET':
        service = ProductService()
        product = service.getProductDetails(product_id)

        if product is None:
            return Response({"status": "error", "message": "Product not found"}, status=404)

        return Response({"status": "ok", "data": product})

    if request.method == 'PATCH':
        return products_patch_handler(request, product_id)
    