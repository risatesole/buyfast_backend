from django.contrib import admin
from .models import Genre, Author, Publisher, Book, BookImage


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("fullname",)
    search_fields = ("fullname",)


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class BookImageInline(admin.TabularInline):
    model = BookImage
    extra = 1
    fields = ("image_type", "image")


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "publisher", "genre", "isbn", "status", "release_date")
    list_filter = ("status", "genre", "author", "publisher", "release_date")
    search_fields = ("title", "isbn", "synopsis")
    inlines = [BookImageInline]
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("title", "synopsis", "isbn")
        }),
        ("Product & Details", {
            "fields": ("product", "release_date")
        }),
        ("Classification", {
            "fields": ("author", "publisher", "genre")
        }),
        ("Pricing", {
            "fields": ("tax_rate",)
        }),
        ("Status", {
            "fields": ("status",)
        }),
    )


@admin.register(BookImage)
class BookImageAdmin(admin.ModelAdmin):
    list_display = ("book", "image_type", "image")
    list_filter = ("image_type", "book")
    search_fields = ("book__title", "image")
    fieldsets = (
        ("Book & Type", {
            "fields": ("book", "image_type")
        }),
        ("Image", {
            "fields": ("image",)
        }),
    )