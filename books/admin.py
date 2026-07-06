# admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg
from django import forms
from . import models


class AuthorAdmin(admin.ModelAdmin):
    list_display = ['id', 'fullname', 'book_count']
    search_fields = ['fullname']
    ordering = ['fullname']

    def book_count(self, obj):
        return obj.books.count()
    book_count.short_description = 'Number of Books'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(book_count=Count('books'))


class BookImageInline(admin.TabularInline):
    model = models.BookImage
    extra = 1
    max_num = 2
    fields = ['image', 'image_type', 'image_preview']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.image
            )
        return "No image"
    image_preview.short_description = 'Preview'


class TaxRateRangeFilter(admin.SimpleListFilter):
    title = 'Tax Rate'
    parameter_name = 'tax_rate'
    
    def lookups(self, request, model_admin):
        return [
            ('0-5', '0% - 5%'),
            ('5-10', '5% - 10%'),
            ('10-15', '10% - 15%'),
            ('15-20', '15% - 20%'),
            ('20+', '20%+'),
        ]
    
    def queryset(self, request, queryset):
        if self.value():
            if self.value() == '0-5':
                return queryset.filter(tax_rate__lte=0.05)
            elif self.value() == '5-10':
                return queryset.filter(tax_rate__gt=0.05, tax_rate__lte=0.10)
            elif self.value() == '10-15':
                return queryset.filter(tax_rate__gt=0.10, tax_rate__lte=0.15)
            elif self.value() == '15-20':
                return queryset.filter(tax_rate__gt=0.15, tax_rate__lte=0.20)
            elif self.value() == '20+':
                return queryset.filter(tax_rate__gt=0.20)
        return queryset


class BookAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'title', 'author', 'selling_price',
        'purchase_cost', 'profit_margin', 'status',
        'release_date', 'tag_list', 'image_count'
    ]

    list_filter = [
        'status',
        'author',
        'release_date',
        'tags',
        TaxRateRangeFilter,  # Fixed: Use your custom filter
    ]

    search_fields = [
        'title',
        'synopsis',
        'author__fullname',
    ]

    readonly_fields = ['profit_margin']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'synopsis', 'author', 'tags')
        }),
        ('Pricing', {
            'fields': ('selling_price', 'purchase_cost', 'tax_rate', 'profit_margin'),
            'classes': ('wide',)
        }),
        ('Status & Dates', {
            'fields': ('status', 'release_date'),
            'classes': ('collapse',)
        }),
    )

    inlines = [BookImageInline]
    list_select_related = ['author']
    list_per_page = 50

    actions = [
        'activate_books',
        'deactivate_books',
        'increase_price_by_percentage',
        'decrease_price_by_percentage'
    ]

    def profit_margin(self, obj):
        if obj.purchase_cost and obj.selling_price > 0:
            margin = ((obj.selling_price - obj.purchase_cost) / obj.selling_price) * 100
            return f"{margin:.1f}%"
        return "N/A"
    profit_margin.short_description = 'Profit Margin'

    def tag_list(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    tag_list.short_description = 'Tags'

    def image_count(self, obj):
        count = obj.images.count()
        return f"{count}/2"
    image_count.short_description = 'Images'

    def activate_books(self, request, queryset):
        updated = queryset.update(status='ACTIVE')
        self.message_user(request, f'{updated} books were activated.')
    activate_books.short_description = 'Activate selected books'

    def deactivate_books(self, request, queryset):
        updated = queryset.update(status='DEACTIVATED')
        self.message_user(request, f'{updated} books were deactivated.')
    deactivate_books.short_description = 'Deactivate selected books'

    def increase_price_by_percentage(self, request, queryset):
        percentage = 10
        for book in queryset:
            book.selling_price += (book.selling_price * percentage / 100)
            book.save()
        self.message_user(request, f'Prices increased by {percentage}% for {queryset.count()} books.')
    increase_price_by_percentage.short_description = 'Increase price by 10%'

    def decrease_price_by_percentage(self, request, queryset):
        percentage = 10
        for book in queryset:
            book.selling_price -= (book.selling_price * percentage / 100)
            book.save()
        self.message_user(request, f'Prices decreased by {percentage}% for {queryset.count()} books.')
    decrease_price_by_percentage.short_description = 'Decrease price by 10%'

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class BookImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'book', 'image_type', 'image_preview']
    list_filter = ['image_type', 'book__author']
    search_fields = ['book__title', 'image_type']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 150px; max-width: 150px;" />',
                obj.image
            )
        return "No image"
    image_preview.short_description = 'Preview'


# Register models with the default admin site
admin.site.register(models.Author, AuthorAdmin)
admin.site.register(models.Book, BookAdmin)
admin.site.register(models.BookImage, BookImageAdmin)
