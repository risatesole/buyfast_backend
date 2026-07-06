from rest_framework.response import Response
from accounts.accounts import AccountRole
from ..products import ProductService
from inventory.inventory import create_initial_inventory
from mediaupload import upload_file  
from ..models import Product

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



    raw_tags = request.data.getlist("tags")
    tags = []
    for t in raw_tags:
        tags.extend([x.strip() for x in t.split(",") if x.strip()])
        
    initial_inventory: int = request.data.get("initialinventory")
    
    try:
        product = service.setProduct(
            name=request.data.get("name"),
            description=request.data.get("description"),
            category= service.get_category_object(request.data.get("category_id")),
            brand=request.data.get("brand"),
            selling_price=request.data.get("selling_price"),
            purchase_price = request.data.get("purchase_price"),
            status=status,
            tags=tags,
            images=images
        )

        if initial_inventory is not None:
            product_instance = Product.objects.get(id=product["id"])
            create_initial_inventory(product_instance, int(initial_inventory))
            
    except ValueError as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=400
        )

    return Response(
        {"status": "created", "data": product},
        status=201
    )