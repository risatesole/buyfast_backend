from django.db import models
from taggit.managers import TaggableManager

class Product(models.Model):
    class ProductType(models.TextChoices):
        ELECTRONICS = 'electronics', 'Electronics'
        CLOTHING = 'clothing', 'Clothing'
        BOOKS = 'books', 'Books'
        HOME = 'home', 'Home & Garden'
        TOYS = 'toys', 'Toys & Games'
        FOOD = 'food', 'Food & Beverages'
        OTHER = 'other', 'Other'

    class Category(models.TextChoices):
        ELECTRONICS = 'electronics', 'Electronics'
        CLOTHING = 'clothing', 'Clothing'
        BOOKS = 'books', 'Books'
        HOME = 'home', 'Home & Garden'
        TOYS = 'toys', 'Toys & Games'
        FOOD = 'food', 'Food & Beverages'
        BEAUTY = 'beauty', 'Beauty & Personal Care'
        SPORTS = 'sports', 'Sports & Outdoors'
        AUTOMOTIVE = 'automotive', 'Automotive'
        OTHER = 'other', 'Other'

    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        default=Category.OTHER,
        blank=True,
        null=True
    )
    
    product_type = models.CharField(
        max_length=50,
        choices=ProductType.choices,
        default=ProductType.OTHER,
        blank=True,
        null=True
    )
    thumbnail = models.CharField(max_length=1000)
    tags = TaggableManager(blank=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "core_product"

    def __str__(self):
        return self.name
