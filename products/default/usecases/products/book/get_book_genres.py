from django.core.cache import cache
from products.books.models import Genre


def get_all_genres():
    """
    Get all genres with caching.
    Returns a list of Genre objects ordered by name.
    """
    genres = cache.get('all_genres')
    
    if genres is None:
        genres = list(Genre.objects.all().order_by('name'))
        cache.set('all_genres', genres, timeout=3600)  # Cache for 1 hour
    
    return genres


def get_genre_by_slug(slug):
    """
    Get a single genre by its slug.
    Returns: Genre object or None
    """
    try:
        return Genre.objects.get(slug=slug)
    except Genre.DoesNotExist:
        return None


def get_genre_by_id(genre_id):
    """
    Get a single genre by its id.
    Returns: Genre object or None
    """
    try:
        return Genre.objects.get(id=genre_id)
    except Genre.DoesNotExist:
        return None

