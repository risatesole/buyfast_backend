from rest_framework.response import Response
from accounts.accounts import AccountRole
from products.products import ProductService
def products_post_handler(request):
    user = request.user

    service = ProductService()

    if not user.is_authenticated:
        return Response({"status": "error", "message": "Authentication required"}, status=401)

    if user.role != AccountRole.EMPLOYEE.value:
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
            imageurl=request.data.get("imageurl"),
        )
    except ValueError as e:
        return Response({"status": "error", "message": str(e)}, status=400)

    return Response({"status": "created", "data": product}, status=201)
