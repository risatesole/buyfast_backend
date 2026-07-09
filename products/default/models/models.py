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

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")

    name = models.CharField(max_length=500)  # "Red/Medium", "Hardcover"
    description = models.TextField(blank=True)
    slug = models.CharField(max_length=500)
    sku = models.CharField(max_length=500, unique=True)
    
    # Pricing & Tax
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Inventory
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "core_product_variant"
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"

class ProductImage(models.Model):
    class ImageType(models.TextChoices):
        HERO = 'HERO', 'Hero'          # Main/primary image
        DETAIL = 'DETAIL', 'Detail'    # Detail/product shot
        THUMBNAIL = 'THUMBNAIL', 'Thumbnail'
        GALLERY = 'GALLERY', 'Gallery'
        SIZE = 'SIZE', 'Size Guide'
        COLOR = 'COLOR', 'Color Swatch'
        LIFESTYLE = 'LIFESTYLE', 'Lifestyle'
        PACKAGING = 'PACKAGING', 'Packaging'
        OTHER = 'OTHER', 'Other'
    
    product_variant = models.ForeignKey(
        'ProductVariant', 
        on_delete=models.CASCADE, 
        related_name="images"
    )
    image = models.ImageField(upload_to='product_images/')
    image_type = models.CharField(
        max_length=20,
        choices=ImageType.choices,
        default=ImageType.HERO
    )
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)  # For sorting images
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "product_image"
        ordering = ['order', 'uploaded_at']  # Order by order field then upload time
    
    def __str__(self):
        return f"{self.product_variant} - {self.get_image_type_display()}"
