from rest_framework.response import Response
from accounts.accounts import AccountRole
from ..services.book_service import BookService
from mediaupload import upload_file


def books_patch_handler(request, book_id):
    user = request.user

    if not user.is_authenticated:
        return Response(
            {"status": "error", "message": "Authentication required"},
            status=401
        )

    if user.role != AccountRole.EMPLOYEE.value:
        return Response(
            {"status": "error", "message": "Only employees can edit books"},
            status=403
        )

    status = request.data.get("status")
    if status and status not in ["ACTIVE", "DEACTIVATED"]:
        status = None

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

    try:
        book = service.updateBook(
            book_id=book_id,
            title=request.data.get("title"),
            synopsis=request.data.get("synopsis"),
            isbn=request.data.get("isbn"),
            author_id=request.data.get("author_id"),
            publisher_id=request.data.get("publisher_id"),
            genre_id=request.data.get("genre_id"),
            selling_price=request.data.get("selling_price"),
            purchase_cost=request.data.get("purchase_cost"),
            tax_rate=request.data.get("tax_rate"),
            status=status,
            release_date=request.data.get("release_date"),
            tags=tags or None,
            images=images or None,
        )
    except ValueError as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=400
        )

    return Response(
        {"status": "updated", "data": book},
        status=200
    )
    
