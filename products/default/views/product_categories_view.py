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
        'priority': 3,
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

    'office': {
        'label': 'Office & School',
        'description': 'Office supplies and school materials',
        'priority': 2,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=400&h=400&fit=crop'
        }
    },
    'pet': {
        'label': 'Pet Supplies',
        'description': 'Food, toys, and accessories for pets',
        'priority': 2,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1517849845537-4d257902454a?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1517849845537-4d257902454a?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1517849845537-4d257902454a?w=400&h=400&fit=crop'
        }
    },
    'health': {
        'label': 'Health',
        'description': 'Health and wellness products',
        'priority': 2,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=400&h=400&fit=crop'
        }
    },
    'jewelry': {
        'label': 'Jewelry',
        'description': 'Rings, necklaces, watches, and accessories',
        'priority': 3,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1617038220319-276d3cfab638?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1617038220319-276d3cfab638?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1617038220319-276d3cfab638?w=400&h=400&fit=crop'
        }
    },
    'baby': {
        'label': 'Baby',
        'description': 'Baby products and accessories',
        'priority': 2,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1515488764276-beab7607c1e6?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1515488764276-beab7607c1e6?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1515488764276-beab7607c1e6?w=400&h=400&fit=crop'
        }
    },
    'music': {
        'label': 'Musical Instruments',
        'description': 'Instruments and music accessories',
        'priority': 1,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=400&h=400&fit=crop'
        }
    },
    'tools': {
        'label': 'Tools & Hardware',
        'description': 'Power tools, hand tools, and hardware',
        'priority': 1,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=400&h=400&fit=crop'
        }
    },
    'gaming': {
        'label': 'Gaming',
        'description': 'Video games, consoles, and accessories',
        'priority': 1,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1493711662062-fa541adb3fc8?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1493711662062-fa541adb3fc8?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1493711662062-fa541adb3fc8?w=400&h=400&fit=crop'
        }
    },
    'travel': {
        'label': 'Travel & Luggage',
        'description': 'Suitcases, backpacks, and travel accessories',
        'priority': 1,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=400&h=400&fit=crop'
        }
    },
    'industrial': {
        'label': 'Industrial',
        'description': 'Industrial equipment and supplies',
        'priority': 1,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?w=400&h=400&fit=crop'
        }
    },
    'art': {
        'label': 'Arts & Crafts',
        'description': 'Art supplies and craft materials',
        'priority': 1,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=400&h=400&fit=crop'
        }
    }
}

@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def product_categories_api_view(request):

    return Response({"status": "ok", "data": PRODUCT_CATEGORIES})
