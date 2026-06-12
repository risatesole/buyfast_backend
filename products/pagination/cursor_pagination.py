# products/cursor_pagination.py
#
# Lightweight cursor pagination that works alongside your existing
# offset/limit, sort, search, tags, and category_id query params.
#
# Cursor format:  base64( "<last_id>" )
# We use the product `id` as the cursor because:
#   - It's always unique and indexed
#   - It survives inserts/deletes without drifting (unlike offset)
#   - Works with any sort order when combined with a tie-breaker

import base64
from typing import Optional


# ── Encode / decode ──────────────────────────────────────────────────────────

def encode_cursor(product_id: int) -> str:
    """Turn a product id into a URL-safe cursor string."""
    raw = str(product_id).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def decode_cursor(cursor: str) -> Optional[int]:
    """
    Decode a cursor string back into a product id.
    Returns None if the cursor is missing or malformed.
    """
    if not cursor:
        return None
    # Re-add stripped padding
    padding = 4 - len(cursor) % 4
    cursor += "=" * (padding % 4)
    try:
        return int(base64.urlsafe_b64decode(cursor).decode("utf-8"))
    except (ValueError, Exception):
        return None


# ── Core paginator ───────────────────────────────────────────────────────────

def paginate_queryset(
    queryset,
    cursor: Optional[str],
    page_size: int,
    request,
    url_path: str,
    extra_params: dict,
):
    """
    Slice a queryset using cursor pagination.

    Parameters
    ----------
    queryset    : A Django QuerySet already filtered and ordered by `id`.
                  Must be ordered — add .order_by("-id") before calling.
    cursor      : Raw cursor string from the request (may be None / empty).
    page_size   : How many items to return per page.
    request     : The DRF request (used to build absolute URLs).
    url_path    : The path part of the URL, e.g. "/api/v1/products/".
    extra_params: Dict of the other active query params (tags, sort, etc.)
                  so we can embed them in the next/previous URLs.

    Returns
    -------
    {
        "next":     str | None,   # full URL with cursor for the next page
        "previous": str | None,   # full URL with cursor for the previous page
        "results":  list,         # the serialised items — caller fills this in
        "_queryset_slice": qs,    # the sliced queryset for the caller to serialise
    }
    """
    cursor_id = decode_cursor(cursor) if cursor else None

    # ── Forward pagination (most common) ─────────────────────────────────────
    # We're going from newest → oldest ( order_by("-id") ),
    # so "next page" means IDs *less than* the last one we saw.
    if cursor_id is not None:
        page_qs = queryset.filter(id__lt=cursor_id)
    else:
        page_qs = queryset

    # Fetch one extra item to know whether a next page exists
    items = list(page_qs[: page_size + 1])
    has_next = len(items) > page_size
    page_items = items[:page_size]

    # ── Build next cursor ─────────────────────────────────────────────────────
    next_url = None
    if has_next and page_items:
        last_id = page_items[-1].id
        next_url = _build_cursor_url(request, url_path, encode_cursor(last_id), extra_params)

    # ── Build previous cursor ─────────────────────────────────────────────────
    # "Previous" only makes sense when we're not on the first page
    previous_url = None
    if cursor_id is not None and page_items:
        first_id = page_items[0].id
        previous_url = _build_cursor_url(
            request, url_path, encode_cursor(first_id), extra_params, direction="prev"
        )

    return {
        "next": next_url,
        "previous": previous_url,
        "_page_items": page_items,   # raw model instances
    }


# ── URL builder ───────────────────────────────────────────────────────────────

def _build_cursor_url(request, path: str, cursor: str, extra_params: dict, direction: str = "next") -> str:
    """Assemble a full absolute URL including the cursor and any active filters."""
    from urllib.parse import urlencode

    params = {k: v for k, v in extra_params.items() if v is not None}
    params["cursor"] = cursor
    if direction == "prev":
        params["direction"] = "prev"

    base = request.build_absolute_uri(path)
    return f"{base}?{urlencode(params)}"
