from rest_framework.response import Response
from accounts.accounts import AccountRole
from books.services.book_service import BookService
from products.default.products import ProductService

from mediaupload import upload_file


def books_post_handler(request):
    user = request.user

    if not user.is_authenticated:
        return Response(
            {"status": "error", "message": "Authentication required"},
            status=401
        )

    if user.role != AccountRole.EMPLOYEE.value:
        return Response(
            {"status": "error", "message": "Only employees can create books"},
            status=403
        )

    # Handle status: Accept "ACTIVE" or "DEACTIVATED"
    status = request.data.get("status", "ACTIVE")
    if status not in ["ACTIVE", "DEACTIVATED"]:
        status = "ACTIVE"

    # Build images list from uploaded files
    # Client sends: images_FRONT_COVER, images_BACK_COVER, etc.
    IMAGE_TYPES = ["FRONT_COVER", "BACK_COVER"]
    images = []
    for image_type in IMAGE_TYPES:
        file = request.FILES.get(f"images_{image_type}")
        if file:
            url = upload_file(file)
            images.append({"url": url, "type": image_type})

    service = BookService()

    raw_tags = request.data.getlist("tags")
    tags = []
    for t in raw_tags:
        tags.extend([x.strip() for x in t.split(",") if x.strip()])
    
    product_service = ProductService()

    try:
        product = product_service.setProduct(
            title=request.data.get("title"),
            description= request.data.get("synopsis"),
            category_id = None, # todo set book product category
            brand = None,
            selling_price = request.data.get("selling_price"),
            status = status,
            tags=tags,
            images=None
        )

        book = service.setBook(
            title=request.data.get("title"),
            synopsis=request.data.get("synopsis"),
            isbn=request.data.get("isbn"),
            author_id=request.data.get("author_id"),
            publisher_id=request.data.get("publisher_id"),
            genre_id=request.data.get("genre_id"),
            selling_price=request.data.get("selling_price"),
            purchase_cost=request.data.get("purchase_cost"),
            tax_rate=request.data.get("tax_rate", 0.18),
            status=status,
            release_date=request.data.get("release_date"),
            tags=tags,
            images=images
        )

    except ValueError as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=400
        )

    return Response(
        {"status": "created", "data": book},
        status=201
    )
    
