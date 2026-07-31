from rest_framework import serializers
from django.db.models import Sum
from products.default.models import ProductVariant
from products.default.models.product_model import Product
from inventory.models import StockMovement_model

class ProductInventorySerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id')
    product_name = serializers.CharField(source='product.name')
    product_description = serializers.CharField(source='product.description', required=False, allow_blank=True)
    variant_id = serializers.IntegerField(source='id')
    thumbnail = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()
    inventory_status = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductVariant
        fields = [
            'variant_id',           # Variant ID
            'product_id',           # Product ID
            'product_name', 
            'product_description', 
            'thumbnail', 
            'quantity',
            'inventory_status',
            'images',
            'sku', 
            'variantnumber', 
            'status',
            'selling_price'
        ]
    
    def get_thumbnail(self, obj):
        """
        Get the primary thumbnail from variant images
        Prioritizes HERO type, then THUMBNAIL, then first available image
        """
        # Get all images for this variant
        images = obj.images.all()
        
        if images.exists():
            # Try to get HERO image first
            hero_image = images.filter(image_type='HERO').first()
            if hero_image:
                return hero_image.image
            
            # Then try THUMBNAIL
            thumbnail_image = images.filter(image_type='THUMBNAIL').first()
            if thumbnail_image:
                return thumbnail_image.image
            
            # Finally, get the first image ordered by order field
            first_image = images.order_by('order', 'uploaded_at').first()
            if first_image:
                return first_image.image
        
        # If no variant images, check product thumbnail
        if obj.product.thumbnail:
            return obj.product.thumbnail
        
        return None
    
    def get_images(self, obj):
        """
        Get all images for the variant with their details
        """
        images = obj.images.all().order_by('order', 'uploaded_at')
        return [
            {
                'id': img.id,
                'image': img.image,
                'image_type': img.image_type,
                'alt_text': img.alt_text,
                'order': img.order
            }
            for img in images
        ]
    
    def get_quantity(self, obj):
        """
        Calculate total quantity from stock movements
        """
        total_quantity = StockMovement_model.objects.filter(
            product_variant=obj
        ).aggregate(total=Sum('balance'))['total']
        return total_quantity if total_quantity is not None else 0
    
    def get_inventory_status(self, obj):
        """
        Determine inventory status based on quantity
        """
        quantity = self.get_quantity(obj)
        
        if quantity <= 0:
            return 'out_of_stock'
        elif quantity <= 10:
            return 'low_stock'
        elif quantity <= 50:
            return 'medium_stock'
        else:
            return 'in_stock'