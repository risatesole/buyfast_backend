from django.db import models

class Product(models.Model):

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("DEACTIVATED", "Deactivated"),
    ]

    CATEGORY_CHOICE = [
        ("FRUITS_AND_VEGETABLES", "Frutas y vegetales"),
        ("LACTEOUS", "Lacteos"),
        ("GROCERY_AND_GOURMET", "Grocery & Gourmet Food"),

        ("ELECTRONIC_AND_TECH", "Electronics & Tech"),
        ("CLOTHING", "Clothing"),
        ("SHOES", "Shoes"),
        ("JEWELRY", "Jewelry"),

        ("HOME_AND_KITCHEN", "Home & Kitchen"),
        ("TOOLS_AND_HOME_IMPROVEMENT", "Tools & Home Improvement"),
        ("FURNITURE", "Furniture"),

        ("BOOKS", "Books"),
        ("VIDEO_GAMES", "Video Games"),
        ("MUSIC", "Music"),
        ("MOVIES_AND_TV", "Movies & TV"),

        ("BEAUTY_AND_PERSONAL_CARE", "Beauty & Personal Care"),
        ("HEALTH_AND_HOUSEHOLD", "Health & Household"),

        ("TOYS_AND_GAMES", "Toys & Games"),
        ("BABY_PRODUCTS", "Baby Products"),

        ("SPORTS_AND_OUTDOORS", "Sports & Outdoors"),
        ("AUTOMOTIVE", "Automotive"),

        ("PET_SUPPLIES", "Pet Supplies"),
        ("OFFICE_PRODUCTS", "Office Products"),
        ("INDUSTRIAL_AND_SCIENTIFIC", "Industrial & Scientific"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()

    category = models.CharField(
        max_length=40,
        choices=CATEGORY_CHOICE
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ACTIVE"
    )

    brand = models.CharField(max_length=255)

    image = models.ImageField(
        upload_to="products/",
        null=True,
        blank=True
    )
    
    METRIC_UNIT_CHOICES = [
        ("UNIT", "Unit"),
        ("PAIR", "Shoe pair"),
        ("BOX","Box")
    ]

    metric_unit = models.CharField(
        max_length=10,
        choices=METRIC_UNIT_CHOICES,
        default="UNIT"
    )

    def __str__(self):
        return self.name
