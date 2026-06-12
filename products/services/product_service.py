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

        qs = self.getProductQueryset(
            status=status,
            sort=sort,
            search=search,
            tags=tags,
            category_id=category_id,
        )

        MAX_LIMIT = 100
        DEFAULT_LIMIT = 20
        MAX_OFFSET = 10000

        limit = min(limit, MAX_LIMIT) if limit else DEFAULT_LIMIT
        offset = min(int(offset), MAX_OFFSET)

        return [self._serialize(p) for p in qs[offset:offset + limit]]

    def getProductQueryset(self, status=None, sort=None, search=None,
                           tags=None, category_id=None):
        """
        Returns a filtered, ordered QuerySet of Product instances.
        Does NOT slice — used by cursor pagination and getProductViaQuery.
        Always includes -id as a stable tie-breaker for consistent pagination.
        """
        ALLOWED_SORT_FIELDS = {"id", "name", "selling_price", "brand", "category__name"}

        qs = Product.objects.select_related("category").prefetch_related("images", "tags")

        if status is not None:
            qs = qs.filter(status=status)

        if category_id is not None:
            qs = qs.filter(category_id=category_id)

        if search and len(search) >= 2:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(brand__icontains=search) |
                Q(category__name__icontains=search) |
                Q(tags__name__icontains=search)
            ).distinct()

        if tags:
            qs = qs.filter(tags__name__in=tags).distinct()

        if sort:
            field = sort.lstrip("-")
            if field in ALLOWED_SORT_FIELDS:
                # Always append -id as a tie-breaker so cursor position is stable
                qs = qs.order_by(sort, "-id")
        else:
            qs = qs.order_by("-id")

        return qs

    def serializeProducts(self, products):
        """
        Serializes a list or queryset slice of Product instances.
        Reuses _serialize so the shape is identical to getProductViaQuery.
        """
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

            "images": [
                {
                    "url": img.image,
                    "type": img.image_type
                }
                for img in product.images.all()
            ],

            "tags": list(product.tags.names())
        }

    def updateProduct(self, product_id, name=None, description=None,
                    category_id=None, brand=None, selling_price=None,
                    status=None, tags=None, images=None):

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ValueError(f"Product with id {product_id} does not exist")

        if name is not None:
            product.name = name
        if description is not None:
            product.description = description
        if brand is not None:
            product.brand = brand
        if selling_price is not None:
            product.selling_price = selling_price
        if status is not None:
            product.status = status

        if category_id is not None:
            try:
                product.category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                raise ValueError(f"Category with id {category_id} does not exist")

        product.save()

        if tags is not None:
            product.tags.set(tags)

        if images:
            for img in images:
                ProductImage.objects.update_or_create(
                    product=product,
                    image_type=img.get("type"),
                    defaults={"image": img.get("url")},
                )

        return self._serialize(product)
    