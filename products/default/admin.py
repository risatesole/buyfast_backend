from django.contrib import admin
from .models import Category, ProductType, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "status")
    list_filter = ("status",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "slug", "description")
        }),
        ("Display", {
            "fields": ("image", "status")
        }),
    )


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "slug", "description")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    readonly_fields = ("created_at", "updated_at")


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image_type", "image", "image_small", "image_medium", "image_large")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "category", "product_type", "selling_price", "metric_unit", "status")
    list_filter = ("status", "category", "product_type", "metric_unit")
    search_fields = ("name", "brand", "description")
    inlines = [ProductImageInline]
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "description", "brand")
        }),
        ("Classification", {
            "fields": ("category", "product_type")
        }),
        ("Pricing & Metrics", {
            "fields": ("selling_price", "metric_unit", "tax_rate")
        }),
        ("Media", {
            "fields": ("thumbnail",)
        }),
        ("Status", {
            "fields": ("status",)
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "image_type", "image")
    list_filter = ("image_type", "product")
    search_fields = ("product__name", "image")
    fieldsets = (
        ("Product & Type", {
            "fields": ("product", "image_type")
        }),
        ("Image URLs", {
            "fields": ("image", "image_small", "image_medium", "image_large")
        }),
    )
