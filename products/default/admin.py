from django.contrib import admin
from .models import Category, ProductType, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


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


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "created_at",
        "updated_at",
    )
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "brand",
        "category",
        "product_type",
        "selling_price",
        "metric_unit",
        "status",
    )
    list_filter = (
        "status",
        "category",
        "product_type",
        "metric_unit",
    )
    search_fields = (
        "name",
        "brand",
        "description",
    )
    autocomplete_fields = (
        "category",
        "product_type",
    )
    list_select_related = (
        "category",
        "product_type",
    )
    inlines = [ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "image_type",
    )
    list_filter = ("image_type",)
    search_fields = (
        "product__name",
        "image",
    )
    autocomplete_fields = ("product",)
