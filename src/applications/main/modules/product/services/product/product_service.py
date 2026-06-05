from .....models import Product
from django.db.models import Q

class ProductService:
    """
    Service layer for handling Product-related operations.

    This class provides methods to retrieve and create Products
    using the underlying Product model.
    """

    def getProducts(self) -> list[dict]:
        products = Product.objects.all()

        return [
            {
                "id": product.id, # type: ignore
                "name": product.name,
                "description": product.description,
                "category": product.category,
                "image": product.image if product.image else None,
                "brand": product.brand,
                "selling_price": product.selling_price,
                "status": product.status
            }
            for product in products
        ]
    
    def getProductViaQuery(
        self,
        status=None,
        sort=None,
        limit=None,
        offset=0,
        search=None,
    ) -> list[dict]:
        MAX_LIMIT = 100
        DEFAULT_LIMIT = 20

        products = Product.objects.all()

        if status is not None:
            products = products.filter(status=status)

        if search:
            products = products.filter(
                Q(name__icontains=search) |
                Q(brand__icontains=search) |
                Q(category__icontains=search)
            )

        if sort:
            products = products.order_by(sort)

        limit = min(limit, MAX_LIMIT) if limit is not None else DEFAULT_LIMIT
        products = products[offset:offset + limit]

        return [
            {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "category": product.category,
                "image": product.image if product.image else None,
                "brand": product.brand,
                "selling_price": product.selling_price,
                "status": product.status
            }
            for product in products
        ]

    def setProduct(self, name, description, category, brand,selling_price, status):
        product = Product.objects.create(
            name=name,
            description=description,
            category=category,
            brand = brand,
            selling_price = selling_price,
            status = status
        )

        return {
            "id": product.id, # type: ignore
            "name": product.name,
            "description": product.description,
            "category": product.category,
            "brand": product.brand,
            "selling_price": selling_price,
            "status": status
        }

    def setProductPrice(self, product_id, selling_price):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return None

        product.selling_price = selling_price
        product.save()

        return {
            "id": product.id, # type: ignore
            "selling_price": product.selling_price
        }
