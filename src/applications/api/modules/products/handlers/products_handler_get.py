from src.applications.main.modules.product.services.product.product_service import ProductService

def products_get_handler(request):
    service = ProductService()

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
    
    return {
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
    }
