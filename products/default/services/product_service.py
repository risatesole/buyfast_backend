from django.db.models import Q
# from ..models import Category, Product, ProductType
from .serializer.product_serializer import product_serializer

class ProductService:


    def setProduct(self, name, description, category = None, brand=None,
                   selling_price=None, purchase_price =  None, status=None, tags=None, images=None):
        pass


    def getProductDetails(self, id):
        pass


    def getProductViaQuery(self, status=None, sort=None, limit=None,
                           offset=0, tags=None, search=None,
                           category_id=None):
        pass


    def getProductQueryset(self, status=None, sort=None, search=None,
                           tags=None, category_id=None):
        """
        Returns a filtered, ordered QuerySet of Product instances.
        Does NOT slice — used by cursor pagination and getProductViaQuery.
        Always includes -id as a stable tie-breaker for consistent pagination.
        """
        ALLOWED_SORT_FIELDS = {"id", "name", "selling_price", "brand", "category__name"}
        pass
        # qs = Product.objects.select_related("category").prefetch_related("tags")

        # if status is not None:
        #     qs = qs.filter(status=status)

        # if category_id is not None:
        #     qs = qs.filter(category_id=category_id)

        # if search and len(search) >= 2:
        #     qs = qs.filter(
        #         Q(name__icontains=search) |
        #         Q(brand__icontains=search) |
        #         Q(category__name__icontains=search) |
        #         Q(tags__name__icontains=search)
        #     ).distinct()

        # if tags:
        #     qs = qs.filter(tags__name__in=tags).distinct()

        # if sort:
        #     field = sort.lstrip("-")
        #     if field in ALLOWED_SORT_FIELDS:
        #         # Always append -id as a tie-breaker so cursor position is stable
        #         qs = qs.order_by(sort, "-id")
        # else:
        #     qs = qs.order_by("-id")

        # return qs

    def serializeProducts(self, products):
        """
        Serializes a list or queryset slice of Product instances.
        Reuses _serialize so the shape is identical to getProductViaQuery.
        """
        return [self._serialize(p) for p in products]

    def _serialize(self, product):
        return product_serializer(product)

    def updateProduct(self, product_id, name=None, description=None,
                    category_id=None, brand=None, selling_price=None,
                    status=None, tags=None, images=None):
        pass

        # try:
        #     product = Product.objects.get(id=product_id)
        # except Product.DoesNotExist:
        #     raise ValueError(f"Product with id {product_id} does not exist")

        # if name is not None:
        #     product.name = name
        # if description is not None:
        #     product.description = description
        # if brand is not None:
        #     product.brand = brand
        # if selling_price is not None:
        #     product.selling_price = selling_price
        # if status is not None:
        #     product.status = status

        # if category_id is not None:
        #     try:
        #         product.category = Category.objects.get(id=category_id)
        #     except Category.DoesNotExist:
        #         raise ValueError(f"Category with id {category_id} does not exist")

        # product.save()

        # if tags is not None:
        #     product.tags.set(tags)
        # return self._serialize(product)