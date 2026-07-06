from django.contrib import admin
from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "status",
    )
    list_filter = ("status",)
    search_fields = (
        "name",
        "slug",
    )
    prepopulated_fields = {
        "slug": ("name",)
    }


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "brand",
        "selling_price",
        "metric_unit",
        "status",
    )
    list_filter = (
        "status",
        "category",
        "metric_unit",
    )
    search_fields = (
        "name",
        "brand",
        "description",
    )
    autocomplete_fields = ("category",)
    inlines = [ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "image_type",
        "image",
    )
    list_filter = ("image_type",)
    search_fields = (
        "product__name",
        "image",
    )
    
