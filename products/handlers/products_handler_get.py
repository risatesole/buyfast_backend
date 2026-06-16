# products/handlers/products_handler_get.py
#
# Drop-in replacement for your existing handler.
# ─ Old behaviour (offset/limit) still works when no `cursor` param is sent.
# ─ New cursor behaviour activates when `cursor` is present in query params.

from products.products import ProductService
# The path your view is mounted at — used to build next/previous URLs.
# Update this if your urls.py uses a different prefix.
PRODUCTS_URL_PATH = "/api/v1/products/"


def products_get_handler_get(request):
    service = ProductService()

    # ── Parse shared query params ─────────────────────────────────────────────
    sort        = request.query_params.get("sort")
    status_raw  = request.query_params.get("status")
    search      = request.query_params.get("search")
    category_id = request.query_params.get("category_id")
    tags_raw    = request.query_params.get("tags")
    limit       = request.query_params.get("limit")
    limit = int(limit) if limit else None

    # Legacy offset (only used when no cursor is present)
    offset      = int(request.query_params.get("offset", 0))

    # Coerce status
    if status_raw == "true":
        status = True
    elif status_raw == "false":
        status = False
    else:
        status = None

    # Coerce tags
    tags = tags_raw.split(",") if tags_raw else None

    # ── Legacy offset mode (unchanged) ───────────────────────────────────────
    return {
        "status": "ok",
        "data": service.getProductViaQuery(
            status=status,
            sort=sort,
            limit=limit,
            offset=offset,
            search=search,
            tags=tags,
            category_id=int(category_id) if category_id else None,
        )
    }