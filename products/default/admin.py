from django.contrib import admin
from django.core.exceptions import ValidationError
from .models.product_model import Product
from .models.product_variant_model import ProductVariant
from .models.product_image_model import ProductImage


class ProductImageInline(admin.TabularInline):
    """Inline admin for ProductImages within ProductVariant"""
    model = ProductImage
    extra = 1
    fields = ('image', 'image_type', 'alt_text', 'order')
    ordering = ['order', 'uploaded_at']


class ProductVariantInline(admin.TabularInline):
    """Inline admin for ProductVariants within Product"""
    model = ProductVariant
    extra = 1
    fields = (
        'name',
        'variantnumber',
        'sku',
        'selling_price',
        'tax_rate',
        'description'
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'category',
        'product_type',
        'variant_count',
        'created_at',
        'updated_at'
    )
    list_filter = ('category', 'product_type', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'thumbnail')
        }),
        ('Classification', {
            'fields': ('category', 'product_type')
        }),
        ('Tags', {
            'fields': ('tags',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProductVariantInline]
    
    def variant_count(self, obj):
        """Display the number of variants for this product"""
        return obj.variants.count()
    variant_count.short_description = 'Variants'
    
    def save_model(self, request, obj, form, change):
        """Save the product"""
        super().save_model(request, obj, form, change)
    
    def save_formset(self, request, form, formset, change):
        """Validate that at least one variant exists before saving"""
        super().save_formset(request, form, formset, change)
        
        # Check if product has at least one variant
        if not change:  # Creating new product
            product = form.instance
            if not product.variants.exists():
                raise ValidationError(
                    'A product must have at least one variant. Please add a variant.'
                )


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'name',
        'sku',
        'variantnumber',
        'selling_price',
        'tax_rate',
        'image_count',
        'created_at'
    )
    list_filter = ('product', 'created_at', 'selling_price')
    search_fields = ('name', 'sku', 'product__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Product & Basic Info', {
            'fields': ('product', 'name', 'variantnumber')
        }),
        ('SKU & Slug', {
            'fields': ('sku', 'slug')
        }),
        ('Pricing & Tax', {
            'fields': ('selling_price', 'tax_rate')
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('wide',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProductImageInline]
    
    def image_count(self, obj):
        """Display the number of images for this variant"""
        return obj.images.count()
    image_count.short_description = 'Images'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        'product_variant',
        'image_type',
        'order',
        'alt_text',
        'uploaded_at'
    )
    list_filter = ('image_type', 'uploaded_at')
    search_fields = ('alt_text', 'product_variant__name', 'product_variant__product__name')
    readonly_fields = ('uploaded_at',)
    
    fieldsets = (
        ('Variant & Image', {
            'fields': ('product_variant', 'image')
        }),
        ('Image Details', {
            'fields': ('image_type', 'alt_text', 'order')
        }),
        ('Metadata', {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )
