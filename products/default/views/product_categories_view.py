from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
PRODUCT_CATEGORIES = {
    'electronics': {
        'label': 'Electronics',
        'description': 'Electronic devices and gadgets',
        'priority': 3,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1550355291-bbee04a92027?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1550355291-bbee04a92027?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1550355291-bbee04a92027?w=400&h=400&fit=crop'
        }
    },
    'clothing': {
        'label': 'Clothing',
        'description': 'Apparel and fashion items',
        'priority': 3,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=400&fit=crop'
        }
    },
    'books': {
        'label': 'Books',
        'description': 'Books and reading materials',
        'priority': 2,
        'images': {
            'banner': 'https://images.unsplash.com/photo-150784272343-583f20270319?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1507842872343-583f20270319?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1507842872343-583f20270319?w=400&h=400&fit=crop'
        }
    },
    'home': {
        'label': 'Home & Garden',
        'description': 'Home decor and garden supplies',
        'priority': 1,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&h=400&fit=crop'
        }
    },
    'toys': {
        'label': 'Toys & Games',
        'description': 'Toys, games, and entertainment',
        'priority': 2,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?w=400&h=400&fit=crop'
        }
    },
    'food': {
        'label': 'Food & Beverages',
        'description': 'Food products and beverages',
        'priority': 1,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1495521821757-a1efb6729352?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1495521821757-a1efb6729352?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1495521821757-a1efb6729352?w=400&h=400&fit=crop'
        }
    },
    'beauty': {
        'label': 'Beauty & Personal Care',
        'description': 'Beauty and personal care products',
        'priority': 2,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1596462502413-b55a833db978?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1596462502413-b55a833db978?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1596462502413-b55a833db978?w=400&h=400&fit=crop'
        }
    },
    'sports': {
        'label': 'Sports & Outdoors',
        'description': 'Sports equipment and outdoor gear',
        'priority': 2,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=400&h=400&fit=crop'
        }
    },
    'automotive': {
        'label': 'Automotive',
        'description': 'Automotive parts and accessories',
        'priority': 3,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1552820728-8ac41f1ce891?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1552820728-8ac41f1ce891?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1552820728-8ac41f1ce891?w=400&h=400&fit=crop'
        }
    },
    'other': {
        'label': 'Other',
        'description': 'Other miscellaneous items',
        'priority': 3,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1563861826100-9cb868fdbe1c?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1563861826100-9cb868fdbe1c?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1563861826100-9cb868fdbe1c?w=400&h=400&fit=crop'
        }
    },
}

@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def product_categories_api_view(request):

    return Response({"status": "ok", "data": PRODUCT_CATEGORIES})
