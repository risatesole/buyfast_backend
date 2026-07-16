from typing import Dict, TypedDict
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.request import Request

# Definición estricta de interfaces para validación estática (mypy)
class CategoryImage(TypedDict):
    banner: str
    cart: str
    default: str

class Category(TypedDict):
    label: str
    description: str
    priority: int
    images: CategoryImage

# Categorías adaptadas al dominio de un economato universitario
UASD_CATEGORIES: Dict[str, Category] = {
    'stationery': {
        'label': 'Papelería y Suministros',
        'description': 'Cuadernos, bolígrafos, papel y material gastable',
        'priority': 1,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=400&h=400&fit=crop'
        }
    },
    'books_manuals': {
        'label': 'Libros y Manuales',
        'description': 'Textos universitarios, manuales de laboratorio y guías',
        'priority': 1,
        'images': {
            'banner': 'https://images.unsplash.com/photo-150784272343-583f20270319?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1507842872343-583f20270319?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1507842872343-583f20270319?w=400&h=400&fit=crop'
        }
    },
    'medical_lab': {
        'label': 'Medicina y Laboratorio',
        'description': 'Estetoscopios, batas médicas, kits de disección y bioseguridad',
        'priority': 1,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=400&h=400&fit=crop'
        }
    },
    'architecture_arts': {
        'label': 'Arquitectura y Artes',
        'description': 'Reglas T, escalímetros, maquetas, pinturas y pinceles',
        'priority': 2,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=400&h=400&fit=crop'
        }
    },
    'electronics': {
        'label': 'Electrónica y Calculadoras',
        'description': 'Calculadoras científicas, memorias USB y accesorios periféricos',
        'priority': 2,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1550355291-bbee04a92027?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1550355291-bbee04a92027?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1550355291-bbee04a92027?w=400&h=400&fit=crop'
        }
    },
    'uniforms': {
        'label': 'Uniformes e Institucional',
        'description': 'T-shirts UASD, ropa deportiva y promocionales',
        'priority': 3,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=400&fit=crop'
        }
    },
    'snacks_beverages': {
        'label': 'Snacks y Bebidas',
        'description': 'Comida rápida, café, agua y meriendas',
        'priority': 3,
        'images': {
            'banner': 'https://images.unsplash.com/photo-1495521821757-a1efb6729352?w=1200&h=400&fit=crop',
            'cart': 'https://images.unsplash.com/photo-1495521821757-a1efb6729352?w=100&h=100&fit=crop',
            'default': 'https://images.unsplash.com/photo-1495521821757-a1efb6729352?w=400&h=400&fit=crop'
        }
    }
}

@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def product_categories_api_view(request: Request) -> Response:
    """
    Endpoint de solo lectura para obtener las categorías del economato.
    Caché a nivel de frontend (Next.js) fuertemente recomendada.
    """
    return Response({
        "status": "ok",
        "data": UASD_CATEGORIES
    })