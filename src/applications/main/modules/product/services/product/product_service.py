from .....models import Product

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
                "image": product.image.url if product.image else None,
                "brand": product.brand
            }
            for product in products
        ]

    def setProduct(self, name, description, category, brand,selling_price):
        product = Product.objects.create(
            name=name,
            description=description,
            category=category,
            brand = brand,
            selling_price = selling_price
        )
        return {
            "id": product.id, # type: ignore
            "name": product.name,
            "description": product.description,
            "category": product.category,
            "brand": product.brand,
            "selling_price": selling_price,
        }
