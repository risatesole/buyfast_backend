from ...models import  Category
from django.utils.text import slugify

def get_category_books_model_object():
    category, created = Category.objects.get_or_create(
        name="Books",
        defaults={
            'slug': slugify("Books"),
            'description': "All books that fill voids in heart",
            'image': "https://example.com/books-category.jpg",
            'status': True
        }
    )
    return category
