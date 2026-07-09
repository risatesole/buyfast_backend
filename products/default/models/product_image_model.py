from django.db import models

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
