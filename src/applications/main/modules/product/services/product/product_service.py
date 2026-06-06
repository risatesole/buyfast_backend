from .....models import Product
from .....modules.product.models.category_model import Category
from django.db.models import Q

class ProductService:

    def getProductViaQuery(
        self,
        status=None,
        sort=None,
        limit=None,
        offset=0,
        tags=None,
        search=None,
        category_id=None,
    ) -> list[dict]:
        MAX_LIMIT = 100
        DEFAULT_LIMIT = 20
        MAX_OFFSET = 10_000
        ALLOWED_SORT_FIELDS = {"id", "name", "selling_price", "category__name", "brand"}

        products = Product.objects.select_related("category").all()

        if status is not None:
            products = products.filter(status=status)

        if category_id is not None:
            products = products.filter(category__id=category_id)

        if search and len(search) >= 2:
            products = products.filter(
                Q(name__icontains=search) |
                Q(brand__icontains=search) |
                Q(category__name__icontains=search) |
                Q(tags__name__icontains=search)
            ).distinct()

        if tags:
            products = products.filter(tags__name__in=tags).distinct()

        if sort:
            field = sort.lstrip("-")
            if field in ALLOWED_SORT_FIELDS:
                products = products.order_by(sort)

        limit = min(limit, MAX_LIMIT) if limit is not None else DEFAULT_LIMIT
        offset = min(int(offset), MAX_OFFSET)
        products = products[offset:offset + limit]

        return [self._serialize(product) for product in products]

    def setProduct(self, name, description, category_id, brand, selling_price, status, tags):
        if not category_id:
            raise ValueError("category_id is required")

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            raise ValueError(f"Category with id {category_id} does not exist")

        product = Product.objects.create(
            name=name,
            description=description,
            category=category,
            brand=brand,
            selling_price=selling_price,
            status=status,
        )

        if tags:
            product.tags.set(tags)

        return self._serialize(product)

    def setProductPrice(self, product_id, selling_price):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return None

        product.selling_price = selling_price
        product.save()

        return {
            "id": product.id,
            "selling_price": product.selling_price
        }

    def _serialize(self, product) -> dict:
        return {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "category": {
                "id": product.category.id,
                "name": product.category.name,
                "slug": product.category.slug,
                "image": product.category.image or None,
                "status": product.category.status,
            } if product.category else None,
            "image": product.image or None,
            "brand": product.brand,
            "selling_price": product.selling_price,
            "status": product.status,
            "tags": list(product.tags.names()),
        }