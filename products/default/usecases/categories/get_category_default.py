from ...models import  Category
from django.utils.text import slugify

def get_category_default_model_object():
    category, created = Category.objects.get_or_create(
        name="Electronics",
        defaults={
            'slug': slugify("Electronics"),
            'description': "All electronic devices and gadgets",
            'image': "https://example.com/electronics-category.jpg",
            'status': True
        }
    )
    return category
