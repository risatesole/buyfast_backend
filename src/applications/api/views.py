from ..main.modules.product.services.product.product_service import ProductService
from ..main.modules.product.models.model_product import Product
from ..main.models import UserRoles
from .utils import CsrfExemptSessionAuthentication
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.views.decorators.csrf import csrf_exempt

@api_view(['GET'])
def health(request):
    return Response({
        "status": "ok"
    })

@api_view(['GET', 'POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def products(request):
    service = ProductService()

    if request.method == 'GET':
        return Response({
            "status": "ok",
            "data": service.getProducts()
        })

    user = request.user

    if not user.is_authenticated:
        return Response({
            "status": "error",
            "message": "Authentication required"
        }, status=401)

    if user.role != UserRoles.EMPLOYEE.value:
        return Response({
            "status": "error",
            "message": "Only employees can create products"
        }, status=403)

    product = service.setProduct(
        name=request.data.get("name"),
        description=request.data.get("description"),
        category=request.data.get("category"),
        brand=request.data.get("brand"),
    )

    return Response({
        "status": "created",
        "data": product
    }, status=201)



categories = [
    {
        "title": "unknown",
        "description": "N/A"
    },
    {
        "title": "Electronics",
        "description": "Devices, gadgets, and electronic accessories."
    },
    {
        "title": "Computers",
        "description": "Laptops, desktops, components, and peripherals."
    },
    {
        "title": "Smartphones",
        "description": "Mobile phones and related accessories."
    },
    {
        "title": "Home Appliances",
        "description": "Appliances for household use and maintenance."
    },
    {
        "title": "Furniture",
        "description": "Indoor and outdoor furniture for homes and offices."
    },
    {
        "title": "Clothing",
        "description": "Apparel for men, women, and children."
    },
    {
        "title": "Footwear",
        "description": "Shoes, sandals, boots, and other footwear."
    },
    {
        "title": "Beauty & Personal Care",
        "description": "Cosmetics, skincare, and personal hygiene products."
    },
    {
        "title": "Health & Wellness",
        "description": "Health-related products, supplements, and wellness items."
    },
    {
        "title": "Sports & Fitness",
        "description": "Equipment, apparel, and accessories for sports and exercise."
    },
    {
        "title": "Books",
        "description": "Printed books, e-books, and educational materials."
    },
    {
        "title": "Toys & Games",
        "description": "Toys, board games, puzzles, and entertainment products."
    },
    {
        "title": "Automotive",
        "description": "Vehicle parts, accessories, and maintenance products."
    },
    {
        "title": "Pet Supplies",
        "description": "Food, accessories, and care products for pets."
    },
    {
        "title": "Groceries",
        "description": "Food, beverages, and everyday consumables."
    },
    {
        "title": "Office Supplies",
        "description": "Products for office work, organization, and productivity."
    },
    {
        "title": "Garden & Outdoor",
        "description": "Gardening tools, outdoor furniture, and landscaping products."
    },
    {
        "title": "Baby Products",
        "description": "Products for infants, toddlers, and parents."
    },
    {
        "title": "Jewelry & Accessories",
        "description": "Jewelry, watches, and fashion accessories."
    },
    {
        "title": "Tools & Hardware",
        "description": "Hand tools, power tools, and hardware supplies."
    }
]

@api_view(['GET'])
def product_categories(request):
    return Response({
        "status": "ok",
        "data": categories
    })
