from django.db.models import Q
from ..models import Category, Product, ProductImage


class ProductService:

    def setProduct(self, name, description, category_id, brand,
                   selling_price, status, tags=None, images=None):

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

        # ✅ handle images
        if images:
            for img in images:
                ProductImage.objects.create(
                    product=product,
                    image=img.get("url"),
                    image_type=img.get("type", "HERO")
                )

        return self._serialize(product)

    def getProductDetails(self, id):
        try:
            product = Product.objects.select_related("category").get(id=id)
        except Product.DoesNotExist:
            return None

        return self._serialize(product)

    def getProductViaQuery(self, status=None, sort=None, limit=None,
                           offset=0, tags=None, search=None,
                           category_id=None):

        MAX_LIMIT = 100
        DEFAULT_LIMIT = 20
        MAX_OFFSET = 10000

        ALLOWED_SORT_FIELDS = {"id", "name", "selling_price", "brand", "category__name"}

        products = Product.objects.select_related("category").all()

        if status is not None:
            products = products.filter(status=status)

        if category_id is not None:
            products = products.filter(category_id=category_id)

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

        limit = min(limit, MAX_LIMIT) if limit else DEFAULT_LIMIT
        offset = min(int(offset), MAX_OFFSET)

        products = products[offset:offset + limit]

        return [self._serialize(p) for p in products]

    def _serialize(self, product):
        return {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "brand": product.brand,
            "selling_price": float(product.selling_price),
            "status": product.status,

            "category": {
                "id": product.category.id,
                "name": product.category.name,
                "slug": product.category.slug,
                "image": product.category.image,
                "status": product.category.status,
            } if product.category else None,

            # ✅ MULTIPLE IMAGES
            "images": [
                {
                    "url": img.image,
                    "type": img.image_type
                }
                for img in product.images.all()
            ],

            "tags": list(product.tags.names())
        }
