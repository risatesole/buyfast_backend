from ..main.modules.product.services.product.product_service import ProductService
from ..main.modules.product.services.product.category_service import CategoryService
from ..main.modules.product.models.model_product import Product
from ..main.models import UserRoles
from .utils import CsrfExemptSessionAuthentication
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated


@api_view(['GET'])
def health(request):
    return Response({"status": "ok"})


@api_view(['GET', 'POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
def products(request):
    service = ProductService()

    if request.method == 'GET':
        sort = request.query_params.get("sort")
        status = request.query_params.get("status")
        search = request.query_params.get("search")
        limit = request.query_params.get("limit")
        offset = request.query_params.get("offset", 0)
        category_id = request.query_params.get("category_id")

        if status == "true":
            status = True
        elif status == "false":
            status = False
        else:
            status = None

        tags = request.query_params.get("tags")
        tags = tags.split(",") if tags else None

        return Response({
            "status": "ok",
            "data": service.getProductViaQuery(
                status=status,
                sort=sort,
                limit=int(limit) if limit else None,
                offset=int(offset),
                search=search,
                tags=tags,
                category_id=int(category_id) if category_id else None,
            )
        })

    user = request.user

    if not user.is_authenticated:
        return Response({"status": "error", "message": "Authentication required"}, status=401)

    if user.role != UserRoles.EMPLOYEE.value:
        return Response({"status": "error", "message": "Only employees can create products"}, status=403)

    try:
        product = service.setProduct(
            name=request.data.get("name"),
            description=request.data.get("description"),
            category_id=request.data.get("category_id"),
            brand=request.data.get("brand"),
            selling_price=request.data.get("selling_price"),
            status=request.data.get("status"),
            tags=request.data.get("tags", []),
        )
    except ValueError as e:
        return Response({"status": "error", "message": str(e)}, status=400)

    return Response({"status": "created", "data": product}, status=201)


@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def set_product_price(request):
    user = request.user

    if user.role != UserRoles.EMPLOYEE.value:
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
    if user.role != UserRoles.EMPLOYEE.value:
        return Response({"status": "error", "message": "Only employees can create categories"}, status=403)

    category = service.setCategory(
        name=request.data.get("name"),
        slug=request.data.get("slug"),
        description=request.data.get("description", ""),
        image=request.data.get("image", ""),
        status=request.data.get("status", True),
    )
    return Response({"status": "created", "data": category}, status=201)


@api_view(['GET'])
def product_detail(request, product_id):
    service = ProductService()
    product = service.getProductDetails(product_id) # (product_id)  # you may need to check the exact method name in your ProductService

    if product is None:
        return Response({"status": "error", "message": "Product not found"}, status=404)

    return Response({"status": "ok", "data": product})