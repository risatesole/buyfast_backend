from django.db import migrations
from django.utils.text import slugify


def populate_genres(apps, schema_editor):
    """Populate the Genre table with common book genres"""
    Genre = apps.get_model('books', 'Genre')
    
    genres = [
        'Fiction',
        'Non-Fiction',
        'Mystery',
        'Thriller',
        'Romance',
        'Science Fiction',
        'Fantasy',
        'Horror',
        'Biography',
        'History',
        'Self-Help',
        'Business',
        'Children',
        'Young Adult',
        'Poetry',
        'Drama',
        'Adventure',
        'Crime',
        'Literary Fiction',
        'Dystopian',
        'Contemporary',
        'Historical Fiction',
        'Paranormal',
        'Psychology',
        'Philosophy',
        'Art & Design',
        'Cooking',
        'Travel',
        'Religion & Spirituality',
        'Education',
    ]
    
    for genre_name in genres:
        Genre.objects.get_or_create(
            name=genre_name,
            defaults={'slug': slugify(genre_name)}
        )


def reverse_populate_genres(apps, schema_editor):
    """Remove all genres (reverse operation)"""
    Genre = apps.get_model('books', 'Genre')
    Genre.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0007_remove_book_product_book_product_variant'),
    ]

    operations = [
        migrations.RunPython(populate_genres, reverse_populate_genres),
    ]