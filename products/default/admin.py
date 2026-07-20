from django.contrib import admin
from django.utils.html import format_html
from django.db import transaction

# Asegúrate de ajustar las importaciones a la estructura de tu app
from .models.product_model import Product
from .models.product_variant_model import ProductVariant
from .models.product_image_model import ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image_preview', 'image', 'image_type', 'alt_text', 'order')
    readonly_fields = ('image_preview',)
    classes = ('collapse',)

    def image_preview(self, obj: ProductImage) -> str:
        if obj.image:
            return format_html('<img src="{}" style="height: 50px; border-radius: 4px;" />', obj.image)
        return "-"
    image_preview.short_description = "Vista Previa"

class ProductVariantInline(admin.StackedInline):
    model = ProductVariant
    extra = 0
    min_num = 1  # Obliga a que se cree al menos una variante por producto
    prepopulated_fields = {'slug': ('name',)}
    fields = (
        ('name', 'sku'), 
        ('variantnumber', 'slug'), 
        ('selling_price', 'tax_rate'), 
        'description'
    )
    classes = ('collapse',)

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'product_variant', 'image_type', 'order', 'uploaded_at')
    list_filter = ('image_type',)
    search_fields = ('product_variant__sku', 'product_variant__name', 'alt_text')
    list_editable = ('order', 'image_type')
    list_select_related = ('product_variant', 'product_variant__product') # Evita N+1
    
    def image_preview(self, obj: ProductImage) -> str:
        if obj.image:
            return format_html('<img src="{}" style="height: 40px; border-radius: 4px;" />', obj.image)
        return "-"
    image_preview.short_description = "Img"

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('sku', 'product', 'name', 'selling_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('sku', 'name', 'product__name')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    list_select_related = ('product',) # Evita N+1 al consultar la tabla principal

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'product_type', 'thumbnail_preview', 'updated_at')
    list_filter = ('category', 'product_type', 'created_at')
    search_fields = ('name', 'slug', 'variants__sku') # Permite buscar producto por SKU de variante
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductVariantInline]
    
    def thumbnail_preview(self, obj: Product) -> str:
        if obj.thumbnail:
            return format_html('<img src="{}" style="height: 40px; border-radius: 4px;" />', obj.thumbnail)
        return "-"
    thumbnail_preview.short_description = "Thumbnail"

    @transaction.atomic
    def save_related(self, request, form, formsets, change):
        """
        Sobrescribimos save_related porque las variantes (inlines) se guardan aquí.
        Una vez guardada la variante, sincronizamos el thumbnail del Producto
        hacia el modelo ProductImage de su variante principal.
        """
        super().save_related(request, form, formsets, change)
        product = form.instance
        
        if product.thumbnail:
            # Tomamos la variante principal (la de menor variantnumber o la primera creada)
            main_variant = product.variants.order_by('variantnumber', 'id').first()
            
            if main_variant:
                # Sincronización lógica: Actualiza o crea el thumbnail en ProductImage
                ProductImage.objects.update_or_create(
                    product_variant=main_variant,
                    image_type=ProductImage.ImageType.THUMBNAIL,
                    defaults={
                        'image': product.thumbnail,
                        'alt_text': f"Thumbnail para {product.name}",
                        'order': 0
                    }
                )