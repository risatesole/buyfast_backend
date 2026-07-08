from ...models import  Category
from django.utils.text import slugify

def get_category_default_model_object():
    category, created = Category.objects.get_or_create(
        name="default",
        defaults={
            'slug': slugify("default"),
            'description': "basic default category",
            'image': "https://example.com/default-category.jpg",
            'status': True
        }
    )
    return category
