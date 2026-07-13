from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import Product, ProductVariant, ProductImage


class ProductImageInline(admin.TabularInline):
    """Inline admin for Product Images"""
    model = ProductImage
    extra = 1
    fields = ['image', 'image_type', 'alt_text', 'order', 'preview']
    readonly_fields = ['preview']
    ordering = ['order']
    
    def preview(self, obj):
        """Display a preview of the image"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.image
            )
        return "No image"
    preview.short_description = "Preview"


class ProductVariantInline(admin.TabularInline):
    """Inline admin for Product Variants"""
    model = ProductVariant
    extra = 1
    fields = [
        'name', 'variantnumber', 'sku', 'selling_price', 
        'tax_rate', 'slug', 'description'
    ]
    show_change_link = True


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'category', 'product_type', 
        'thumbnail_preview', 'variant_count', 'created_at'
    ]
    list_filter = ['category', 'product_type', 'created_at', 'updated_at']
    search_fields = ['name', 'slug', 'tags__name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'thumbnail_preview']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'product_type')
        }),
        ('Media & Tags', {
            'fields': ('thumbnail', 'thumbnail_preview', 'tags')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProductVariantInline]
    
    actions = ['duplicate_product', 'set_category_electronics', 'set_category_clothing']
    
    def thumbnail_preview(self, obj):
        """Display thumbnail preview in admin"""
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.thumbnail
            )
        return "No thumbnail"
    thumbnail_preview.short_description = "Thumbnail"
    
    def variant_count(self, obj):
        """Count variants for a product"""
        count = obj.variants.count()
        url = reverse('admin:products_default_productvariant_changelist') + f'?product__id__exact={obj.id}'
        return format_html('<a href="{}">{} Variant{}</a>', url, count, '' if count == 1 else 's')
    variant_count.short_description = "Variants"
    
    def get_queryset(self, request):
        """Override queryset to prefetch variants for count"""
        qs = super().get_queryset(request)
        return qs.prefetch_related('variants')
    
    def duplicate_product(self, request, queryset):
        """Duplicate selected products"""
        for product in queryset:
            # Copy product fields
            new_product = Product(
                name=f"{product.name} (Copy)",
                slug=f"{product.slug}-copy",
                category=product.category,
                product_type=product.product_type,
                thumbnail=product.thumbnail,
            )
            # Save the new product to get an ID
            new_product.save()
            # Copy tags
            new_product.tags.set(product.tags.all())
            
            # Copy variants
            for variant in product.variants.all():
                ProductVariant.objects.create(
                    product=new_product,
                    name=variant.name,
                    description=variant.description,
                    variantnumber=variant.variantnumber,
                    slug=f"{variant.slug}-copy",
                    sku=f"{variant.sku}-copy",
                    selling_price=variant.selling_price,
                    tax_rate=variant.tax_rate,
                )
        
        self.message_user(request, f"{queryset.count()} products duplicated successfully.")
    duplicate_product.short_description = "Duplicate selected products"
    
    def set_category_electronics(self, request, queryset):
        """Bulk update category to Electronics"""
        updated = queryset.update(category=Product.Category.ELECTRONICS)
        self.message_user(request, f"{updated} products updated to Electronics.")
    set_category_electronics.short_description = "Set category to Electronics"
    
    def set_category_clothing(self, request, queryset):
        """Bulk update category to Clothing"""
        updated = queryset.update(category=Product.Category.CLOTHING)
        self.message_user(request, f"{updated} products updated to Clothing.")
    set_category_clothing.short_description = "Set category to Clothing"


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'product_link', 'name', 'variantnumber', 
        'sku', 'selling_price', 'tax_rate', 'created_at'
    ]
    list_filter = ['product__category', 'product__product_type', 'created_at']
    search_fields = [
        'name', 'sku', 'slug', 'product__name', 
        'product__slug', 'description'
    ]
    prepopulated_fields = {'slug': ('name', 'sku')}
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Product Relationship', {
            'fields': ('product', 'product_thumbnail_preview')
        }),
        ('Variant Details', {
            'fields': ('name', 'description', 'variantnumber', 'slug', 'sku')
        }),
        ('Pricing & Tax', {
            'fields': ('selling_price', 'tax_rate')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProductImageInline]
    
    list_editable = ['selling_price', 'tax_rate']
    list_per_page = 50
    
    def product_link(self, obj):
        """Create a link to the product in admin"""
        url = reverse('admin:products_default_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = "Product"
    
    def product_thumbnail_preview(self, obj):
        """Display product's thumbnail preview"""
        if obj.product.thumbnail:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.product.thumbnail
            )
        return "No thumbnail"
    product_thumbnail_preview.short_description = "Product Thumbnail"
    
    def get_queryset(self, request):
        """Override queryset to prefetch product"""
        qs = super().get_queryset(request)
        return qs.select_related('product')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'product_variant_link', 'image_type', 'order', 
        'image_preview', 'uploaded_at'
    ]
    list_filter = ['image_type', 'uploaded_at']
    search_fields = [
        'alt_text', 'product_variant__name', 
        'product_variant__product__name'
    ]
    readonly_fields = ['uploaded_at', 'image_preview']
    
    fieldsets = (
        ('Image Details', {
            'fields': ('product_variant', 'image', 'image_preview')
        }),
        ('Metadata', {
            'fields': ('image_type', 'alt_text', 'order')
        }),
        ('Timestamps', {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )
    
    list_editable = ['image_type', 'order']
    list_per_page = 50
    
    actions = ['set_type_hero', 'set_type_gallery', 'set_type_detail']
    
    def product_variant_link(self, obj):
        """Create a link to the product variant in admin"""
        url = reverse('admin:products_default_productvariant_change', args=[obj.product_variant.id])
        return format_html('<a href="{}">{}</a>', url, obj.product_variant.name)
    product_variant_link.short_description = "Variant"
    
    def image_preview(self, obj):
        """Display image preview in admin"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 150px; max-width: 150px;" />',
                obj.image
            )
        return "No image"
    image_preview.short_description = "Image Preview"
    
    def set_type_hero(self, request, queryset):
        """Bulk update image type to Hero"""
        updated = queryset.update(image_type=ProductImage.ImageType.HERO)
        self.message_user(request, f"{updated} images updated to Hero.")
    set_type_hero.short_description = "Set image type to Hero"
    
    def set_type_gallery(self, request, queryset):
        """Bulk update image type to Gallery"""
        updated = queryset.update(image_type=ProductImage.ImageType.GALLERY)
        self.message_user(request, f"{updated} images updated to Gallery.")
    set_type_gallery.short_description = "Set image type to Gallery"
    
    def set_type_detail(self, request, queryset):
        """Bulk update image type to Detail"""
        updated = queryset.update(image_type=ProductImage.ImageType.DETAIL)
        self.message_user(request, f"{updated} images updated to Detail.")
    set_type_detail.short_description = "Set image type to Detail"
