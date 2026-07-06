from django.contrib import admin
from django.utils.html import format_html
from .models import Author, Publisher, Genre, Book, BookImage


class BookImageInline(admin.TabularInline):
    """Inline admin for BookImage to allow editing images within Book admin."""
    model = BookImage
    extra = 1
    fields = ("image", "image_type")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by("image_type")


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Admin interface for Author model."""
    list_display = ("fullname", "book_count")
    search_fields = ("fullname",)
    list_per_page = 25

    def book_count(self, obj):
        """Display the number of books by this author."""
        count = obj.books.count()
        return format_html(
            '<span style="background-color: #417690; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            count
        )
    book_count.short_description = "Books Published"


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    """Admin interface for Publisher model."""
    list_display = ("name", "book_count")
    search_fields = ("name",)
    list_per_page = 25

    def book_count(self, obj):
        """Display the number of books published by this publisher."""
        count = obj.books.count()
        return format_html(
            '<span style="background-color: #6f42c1; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            count
        )
    book_count.short_description = "Books Published"


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Admin interface for Genre model."""
    list_display = ("name", "book_count")
    search_fields = ("name",)
    list_per_page = 25

    def book_count(self, obj):
        """Display the number of books in this genre."""
        count = obj.books.count()
        return format_html(
            '<span style="background-color: #fd7e14; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            count
        )
    book_count.short_description = "Books in Genre"


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Admin interface for Book model."""
    list_display = ("title", "author", "publisher", "genre", "isbn", "status_badge", "release_date", "selling_price", "profit_margin")
    list_filter = ("status", "release_date", "author", "publisher", "genre")
    search_fields = ("title", "synopsis", "author__fullname", "publisher__name", "genre__name", "isbn")
    readonly_fields = ("calculated_profit",)
    inlines = [BookImageInline]

    fieldsets = (
        ("Book Information", {
            "fields": ("title", "author", "isbn", "synopsis", "tags")
        }),
        ("Publication Details", {
            "fields": ("publisher", "genre", "release_date")
        }),
        ("Pricing & Cost", {
            "fields": ("selling_price", "purchase_cost", "tax_rate", "calculated_profit")
        }),
        ("Status", {
            "fields": ("status",)
        }),
    )

    def status_badge(self, obj):
        """Display status as a colored badge."""
        color = "#28a745" if obj.status == "ACTIVE" else "#dc3545"
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Status"

    def calculated_profit(self, obj):
        """Calculate and display profit margin."""
        if obj.purchase_cost and obj.selling_price:
            profit = obj.selling_price - obj.purchase_cost
            profit_percentage = (profit / obj.purchase_cost * 100) if obj.purchase_cost > 0 else 0
            return format_html(
                '${} ({}%)',
                round(profit, 2),
                round(profit_percentage, 2)
            )
        return "—"
    calculated_profit.short_description = "Profit (Amount & %)"

    def profit_margin(self, obj):
        """Display profit margin percentage in list view."""
        if obj.purchase_cost and obj.selling_price:
            profit = obj.selling_price - obj.purchase_cost
            profit_percentage = (profit / obj.purchase_cost * 100) if obj.purchase_cost > 0 else 0
            color = "#28a745" if profit_percentage > 0 else "#dc3545"
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}%</span>',
                color,
                round(profit_percentage, 2)
            )
        return "—"
    profit_margin.short_description = "Margin %"


@admin.register(BookImage)
class BookImageAdmin(admin.ModelAdmin):
    """Admin interface for BookImage model."""
    list_display = ("book", "image_type", "image_preview")
    list_filter = ("image_type", "book__author")
    search_fields = ("book__title",)
    readonly_fields = ("image_preview_large",)

    fieldsets = (
        ("Image Details", {
            "fields": ("book", "image_type", "image")
        }),
        ("Preview", {
            "fields": ("image_preview_large",),
            "classes": ("collapse",)
        }),
    )

    def image_preview(self, obj):
        """Display a small preview of the image in list view."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 50px; max-height: 50px; border-radius: 3px;" alt="{}">',
                obj.image,
                obj.book.title
            )
        return "—"
    image_preview.short_description = "Preview"

    def image_preview_large(self, obj):
        """Display a larger preview in the detail view."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 400px; border-radius: 5px;" alt="{}">',
                obj.image,
                obj.book.title
            )
        return "No image available"
    image_preview_large.short_description = "Image Preview"
