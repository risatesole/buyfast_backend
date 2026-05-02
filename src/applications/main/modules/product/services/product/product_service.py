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
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "category": product.category
            }
            for product in products
        ]

    def setProduct(self, name, description, category):
        product = Product.objects.create(
            name=name,
            description=description,
            category=category
        )
        return {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "category": product.category
        }
    
    def getAllCategories(self):
        categories = [
            {
                "name": "FRUITS_AND_VEGETABLES",
                "slug": "fruits_and_vegetables",
                "image": "https://images.unsplash.com/photo-1593640408182-31c228b78b5b?w=300&h=300&fit=crop",
                "count": "2.4K+ products"
            },
            {
                "name": "Grocery",
                "slug": "grocery",
                "image": "https://images.unsplash.com/photo-1542838132-92c53300491e?w=300&h=300&fit=crop",
                "count": "1.8K+ products"
            },
            {
                "name": "Home & Kitchen",
                "slug": "home",
                "image": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=300&h=300&fit=crop",
                "count": "3.2K+ products"
            },        
            {
                "name": "Shoes",
                "slug": "shoes",
                "image": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=300&h=300&fit=crop",
                "count": "3.2K+ products"
            },
            {
                "name": "Electronics",
                "slug": "electronics",
                "image": "https://images.unsplash.com/photo-1593640408182-31c228b78b5b?w=300&h=300&fit=crop",
                "count": "2.4K+ products"
            },
            {
                "name": "Grocery",
                "slug": "grocery",
                "image": "https://images.unsplash.com/photo-1542838132-92c53300491e?w=300&h=300&fit=crop",
                "count": "1.8K+ products"
            },
            {
                "name": "Home & Kitchen",
                "slug": "home",
                "image": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=300&h=300&fit=crop",
                "count": "3.2K+ products"
            },        
            {
                "name": "Shoes",
                "slug": "shoes",
                "image": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=300&h=300&fit=crop",
                "count": "3.2K+ products"
            },
                    {
                "name": "Electronics",
                "slug": "electronics",
                "image": "https://images.unsplash.com/photo-1593640408182-31c228b78b5b?w=300&h=300&fit=crop",
                "count": "2.4K+ products"
            },     
            {
                "name": "Shoes",
                "slug": "shoes",
                "image": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=300&h=300&fit=crop",
                "count": "3.2K+ products"
            },
            {
                "name": "Electronics",
                "slug": "electronics",
                "image": "https://images.unsplash.com/photo-1593640408182-31c228b78b5b?w=300&h=300&fit=crop",
                "count": "2.4K+ products"
            },
        ]
        # trick i found the [:8] limits the return to just 8 categories... jaja
        return categories
