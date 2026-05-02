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
                "image": "https://images.unsplash.com/photo-1610832958506-aa56368176cf?w=300&h=300&fit=crop",
                "count": "2.4K+ products"
            },
            {
                "name": "LACTEOUS",
                "slug": "lacteous",
                "image": "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=300&h=300&fit=crop",
                "count": "1.1K+ products"
            },
            {
                "name": "GROCERY_AND_GOURMET",
                "slug": "grocery_and_gourmet",
                "image": "https://images.unsplash.com/photo-1542838132-92c53300491e?w=300&h=300&fit=crop",
                "count": "1.8K+ products"
            },
            {
                "name": "ELECTRONIC_AND_TECH",
                "slug": "electronic_and_tech",
                "image": "https://images.unsplash.com/photo-1518779578993-ec3579fee39f?w=300&h=300&fit=crop",
                "count": "2.6K+ products"
            },
            {
                "name": "CLOTHING",
                "slug": "clothing",
                "image": "https://images.unsplash.com/photo-1521334884684-d80222895322?w=300&h=300&fit=crop",
                "count": "3.0K+ products"
            },
            {
                "name": "SHOES",
                "slug": "shoes",
                "image": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=300&h=300&fit=crop",
                "count": "2.2K+ products"
            },
            {
                "name": "JEWELRY",
                "slug": "jewelry",
                "image": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=300&h=300&fit=crop",
                "count": "900+ products"
            },
            {
                "name": "HOME_AND_KITCHEN",
                "slug": "home_and_kitchen",
                "image": "https://images.unsplash.com/photo-1556912173-3bb406ef7e77?w=300&h=300&fit=crop",
                "count": "3.2K+ products"
            },
            {
                "name": "TOOLS_AND_HOME_IMPROVEMENT",
                "slug": "tools_and_home_improvement",
                "image": "https://images.unsplash.com/photo-1581147036324-c1c1c1d5f6b4?w=300&h=300&fit=crop",
                "count": "1.4K+ products"
            },
            {
                "name": "FURNITURE",
                "slug": "furniture",
                "image": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=300&h=300&fit=crop",
                "count": "1.9K+ products"
            },
            {
                "name": "BOOKS",
                "slug": "books",
                "image": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=300&h=300&fit=crop",
                "count": "2.7K+ products"
            },
            {
                "name": "VIDEO_GAMES",
                "slug": "video_games",
                "image": "https://images.unsplash.com/photo-1605902711622-cfb43c4437d1?w=300&h=300&fit=crop",
                "count": "1.5K+ products"
            },
            {
                "name": "MUSIC",
                "slug": "music",
                "image": "https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=300&h=300&fit=crop",
                "count": "1.2K+ products"
            },
            {
                "name": "MOVIES_AND_TV",
                "slug": "movies_and_tv",
                "image": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=300&h=300&fit=crop",
                "count": "1.6K+ products"
            },
            {
                "name": "BEAUTY_AND_PERSONAL_CARE",
                "slug": "beauty_and_personal_care",
                "image": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=300&h=300&fit=crop",
                "count": "2.1K+ products"
            },
            {
                "name": "HEALTH_AND_HOUSEHOLD",
                "slug": "health_and_household",
                "image": "https://images.unsplash.com/photo-1580281657527-47df83f3fbc6?w=300&h=300&fit=crop",
                "count": "1.3K+ products"
            },
            {
                "name": "TOYS_AND_GAMES",
                "slug": "toys_and_games",
                "image": "https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=300&h=300&fit=crop",
                "count": "1.7K+ products"
            },
            {
                "name": "BABY_PRODUCTS",
                "slug": "baby_products",
                "image": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=300&h=300&fit=crop",
                "count": "800+ products"
            },
            {
                "name": "SPORTS_AND_OUTDOORS",
                "slug": "sports_and_outdoors",
                "image": "https://images.unsplash.com/photo-1517649763962-0c623066013b?w=300&h=300&fit=crop",
                "count": "2.0K+ products"
            },
            {
                "name": "AUTOMOTIVE",
                "slug": "automotive",
                "image": "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=300&h=300&fit=crop",
                "count": "1.2K+ products"
            },
            {
                "name": "PET_SUPPLIES",
                "slug": "pet_supplies",
                "image": "https://images.unsplash.com/photo-1517849845537-4d257902454a?w=300&h=300&fit=crop",
                "count": "1.1K+ products"
            },
            {
                "name": "OFFICE_PRODUCTS",
                "slug": "office_products",
                "image": "https://images.unsplash.com/photo-1497032628192-86f99bcd76bc?w=300&h=300&fit=crop",
                "count": "900+ products"
            },
            {
                "name": "INDUSTRIAL_AND_SCIENTIFIC",
                "slug": "industrial_and_scientific",
                "image": "https://images.unsplash.com/photo-1581093458791-9d8f60f9f0c5?w=300&h=300&fit=crop",
                "count": "700+ products"
            }
        ]

        return categories