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
                "category": product.category,
                "image": product.image.url if product.image else None,
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
                "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT0XPSTaSDJBgYcbj7VlJDhgNzHNfUpZoneLfT3Zsslt8q8pBb3gfrBn2w&s=10"

            },
            {
                "name": "LACTEOUS",
                "slug": "lacteous",
                "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTPcFnV0ulelHT__t2Yb35UGvUvi98aEzUCAECtjVmeiSXocZejxfIKH0zJ&s=10"

            },
            {
                "name": "GROCERY_AND_GOURMET",
                "slug": "grocery_and_gourmet",
                "image": "https://images.unsplash.com/photo-1542838132-92c53300491e?w=300&h=300&fit=crop"

            },
            {
                "name": "ELECTRONIC_AND_TECH",
                "slug": "electronic_and_tech",
                "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ36HpcLFWVQhHC4fz-28itLx81FY0t_eTMmfWM5PMCWuKNuKNV0gJBlEIr&s=10"

            },
            {
                "name": "CLOTHING",
                "slug": "clothing",
                "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQs-1HItAij1fRS45XMCqpgKd_3Pbo7FcrFbOQwVBkVbdwa0pRNmMX2Eqo&s=10"

            },
            {
                "name": "SHOES",
                "slug": "shoes",
                "image": "https://www.campusshoes.com/cdn/shop/files/LEVEL_LEVEL_WHT-L.GRY_07_831c7a2c-ff1b-4011-9268-b11f984219c6.webp?v=1757580207",

            },
            {
                "name": "JEWELRY",
                "slug": "jewelry",
                "image": "https://images.hbjo-online.com/webp/sites/azuelos/uploads/images/693d89b4b7880693d89a8122c4_kasbah-web2jpg.jpg",
                "count": "900+ products"
            },
            {
                "name": "HOME_AND_KITCHEN",
                "slug": "home_and_kitchen",
                "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTkx3grb3WqoyLQKcEkzSVxPtlG6am6LJfp8tAsEIsQyw&s=10",
            },
            {
                "name": "TOOLS_AND_HOME_IMPROVEMENT",
                "slug": "tools_and_home_improvement",
                "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTke0YUVuZltlQfJE03PdHUUQhHh6ORSH_e5-lZPmeBk5KmGHjOGofq-Qo&s=10",
            },
            {
                "name": "FURNITURE",
                "slug": "furniture",
                "image": "https://www.lujoluxuryliving.com/cdn/shop/files/Image_5.jpg?crop=center&height=1200&v=1747656940&width=1200"
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
                "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRqBZM0kMM4Y8ZZ71-BChSQsl3lSWllf-3OnazQ40P10w&s=10"
            },
            {
                "name": "MUSIC",
                "slug": "music",
                "image": "https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=300&h=300&fit=crop"
            },
            {
                "name": "MOVIES_AND_TV",
                "slug": "movies_and_tv",
                "image": "https://theenterpriseworld.com/wp-content/uploads/2025/10/1.1-Before-You-Watch-Any-Other-Movie-See-These-20-Highest-Grossing-Movies-of-All-Time.jpg"
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
                "image": "https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=300&h=300&fit=crop"
            },
            {
                "name": "BABY_PRODUCTS",
                "slug": "baby_products",
                "image": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=300&h=300&fit=crop"
            },
            {
                "name": "SPORTS_AND_OUTDOORS",
                "slug": "sports_and_outdoors",
                "image": "https://images.unsplash.com/photo-1517649763962-0c623066013b?w=300&h=300&fit=crop"
            },
            {
                "name": "AUTOMOTIVE",
                "slug": "automotive",
                "image": "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=300&h=300&fit=crop"
            },
            {
                "name": "PET_SUPPLIES",
                "slug": "pet_supplies",
                "image": "https://images.unsplash.com/photo-1517849845537-4d257902454a?w=300&h=300&fit=crop"
            },
            {
                "name": "OFFICE_PRODUCTS",
                "slug": "office_products",
                "image": "https://images.unsplash.com/photo-1497032628192-86f99bcd76bc?w=300&h=300&fit=crop"
            },
            {
                "name": "INDUSTRIAL_AND_SCIENTIFIC",
                "slug": "industrial_and_scientific",
                "image": "https://images.unsplash.com/photo-1581093458791-9d8f60f9f0c5?w=300&h=300&fit=crop"
            }
        ]

        return categories
