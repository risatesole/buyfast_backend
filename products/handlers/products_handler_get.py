# products/handlers/products_handler_get.py
#
# Drop-in replacement for your existing handler.
# ─ Old behaviour (offset/limit) still works when no `cursor` param is sent.
# ─ New cursor behaviour activates when `cursor` is present in query params.

from products.products import ProductService
from products.pagination.cursor_pagination import paginate_queryset, encode_cursor

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

    # Cursor-pagination params
    cursor      = request.query_params.get("cursor")          # encoded cursor
    page_size   = int(request.query_params.get("limit", 20))  # items per page

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

    # ── Cursor mode ───────────────────────────────────────────────────────────
    if cursor is not None or request.query_params.get("paginate") == "cursor":
        # 1. Get the raw filtered + ordered queryset from your service layer.
        #    We need the queryset itself, not a list, so we add a helper below.
        qs = service.getProductQueryset(
            status=status,
            sort=sort,
            search=search,
            tags=tags,
            category_id=int(category_id) if category_id else None,
        )

        # Extra params to re-embed in next/previous URLs
        extra_params = {
            "sort":        sort,
            "status":      status_raw,
            "search":      search,
            "tags":        tags_raw,
            "category_id": category_id,
            "limit":       str(page_size) if page_size != 20 else None,
        }

        page = paginate_queryset(
            queryset=qs,
            cursor=cursor,
            page_size=page_size,
            request=request,
            url_path=PRODUCTS_URL_PATH,
            extra_params=extra_params,
        )

        # Serialise the page items using your existing serialiser
        serialised = service.serializeProducts(page["_page_items"])

        return {
            "next":     page["next"],
            "previous": page["previous"],
            "results":  serialised,
        }

    # ── Legacy offset mode (unchanged) ───────────────────────────────────────
    return {
        "status": "ok",
        "data": service.getProductViaQuery(
            status=status,
            sort=sort,
            limit=page_size,
            offset=offset,
            search=search,
            tags=tags,
            category_id=int(category_id) if category_id else None,
        )
    }