from books.services.book_service import BookService

BOOKS_URL_PATH = "/api/v1/books/"


def books_get_handler(request):
    service = BookService()

    # ── Parse shared query params ─────────────────────────────────────────────
    sort        = request.query_params.get("sort")
    status_raw  = request.query_params.get("status")
    search      = request.query_params.get("search")
    author_id   = request.query_params.get("author_id")
    tags_raw    = request.query_params.get("tags")
    limit       = request.query_params.get("limit")
    limit = int(limit) if limit else None

    # Legacy offset (only used when no cursor is present)
    offset      = int(request.query_params.get("offset", 0))

    # Coerce status
    if status_raw == "ACTIVE":
        status = "ACTIVE"
    elif status_raw == "DEACTIVATED":
        status = "DEACTIVATED"
    else:
        status = None

    # Coerce tags
    tags = tags_raw.split(",") if tags_raw else None

    # ── Legacy offset mode (unchanged) ───────────────────────────────────────
    return {
        "status": "ok",
        "data": service.getBookViaQuery(
            status=status,
            sort=sort,
            limit=limit,
            offset=offset,
            search=search,
            tags=tags,
            author_id=int(author_id) if author_id else None,
        )
    }
