from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def orders_api_view(request,order_id):
    return Response({
        "data": {
            "id": order_id,
            "profilepicture": "https://example.com",
            "firstname": "Jhon",
            "lastname": "Doe",
            "email": "jhon@example.com",
            "created_at": "2026-06-15T14:30:00Z",
            "total": 299.97,
            "status": "penidng",
            "pickup_time": "2026-06-15T14:30:00Z",
            "phone": "+1 (555) 123-4567",
            "address": {
                "street": "123 Main Street",
                "city": "New York",
                "state": "NY",
                "zipCode": "10001",
                "country": "USA"
            },
            "items": [
              {
                "id": 1,
                "product_id": 101,
                "product_name": "Premium Wireless Headphones",
                "quantity": 2,
                "price": 99.99,
                "image_url": "https://zdnhvnvrngxvxedrvuon.supabase.co/storage/v1/object/public/bucket1/uploads/1781315332_zapatos-de-tacon-alto-para-mujer-con-plataforma-con-puntera-abierta-938336.jpg",
                "sku": "WH-1000XM4"
              },
              {
                "id": 2,
                "product_id": 102,
                "product_name": "USB-C Charging Cable",
                "quantity": 3,
                "price": 19.99,
                "image_url": "https://zdnhvnvrngxvxedrvuon.supabase.co/storage/v1/object/public/bucket1/uploads/1781315332_zapatos-de-tacon-alto-para-mujer-con-plataforma-con-puntera-abierta-938336.jpg",
                "sku": "CBL-USBC-01"
              }
            ],
            "shipping_method": "standard_shipping",
            "payment_method": "credit_card",
            "notes": "Please leave at front door"
                }
            })
