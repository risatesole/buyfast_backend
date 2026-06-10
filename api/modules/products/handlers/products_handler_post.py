from rest_framework.response import Response
from accounts.accounts import AccountRole
from products.products import ProductService
from file_storage import upload_file  

def products_post_handler(request):
    user = request.user

    if not user.is_authenticated:
        return Response(
            {"status": "error", "message": "Authentication required"},
            status=401
        )

    if user.role != AccountRole.EMPLOYEE.value:
        return Response(
            {"status": "error", "message": "Only employees can create products"},
            status=403
        )

    raw_status = request.data.get("status")
    status = str(raw_status).lower() in ("true", "1", "yes") if raw_status is not None else True
    
    # Build images list from uploaded files
    # Client sends: images_HERO, images_SCALE, images_FLATLAY, etc.
    IMAGE_TYPES = ["HERO", "SCALE", "PACKING", "FLATLAY", "FREEZE_FRAME"]
    images = []
    for image_type in IMAGE_TYPES:
        file = request.FILES.get(f"images_{image_type}")
        if file:
            url = upload_file(file)
            images.append({"url": url, "type": image_type})

    service = ProductService()

    try:
        product = service.setProduct(
            name=request.data.get("name"),
            description=request.data.get("description"),
            category_id=request.data.get("category_id"),
            brand=request.data.get("brand"),
            selling_price=request.data.get("selling_price"),
            status=status,
            tags=request.data.get("tags", []),
            images=images
        )

    except ValueError as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=400
        )

    return Response(
        {"status": "created", "data": product},
        status=201
    )