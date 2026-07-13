from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status  
from ...models import Order



# WAENING : mock
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def orders_api_view(request, order_id):
    
    try:
        
        order = Order.objects.select_related(
            'customer',
        ).prefetch_related(
            'items__product'
        ).get(id=order_id)
        
        payment_method = None
        # if hasattr(order, 'payment'):
        #     payment_method = order.payment.payment_provider.name

        return Response({
            "data": {
                "id": order.id,
                "profilepicture": order.customer.profile_picture,
                "firstname": order.customer.first_name,
                "lastname": order.customer.last_name,
                "email": order.customer.email,
                "created_at": order.created_at,
                # "total": float(total),
                "status": order.status,
                "pickup_time": order.pickup_time,
                "phone": order.customer.phone_number,
                "address": {
                    "street": "unknown",
                    "city": "unknown",
                    "state": "DO",
                    "zipCode": "00000",
                    "country": "DO"
                },
                "items": [
                    {
                        "id": item.product.id,
                        "name": item.product.name,
                        "quantity": item.quantity,
                        "price": item.price_per_item,
                        "tax": item.tax_amount,
                        "subtotal": (item.price_per_item + item.tax_amount) * item.quantity,
                    }
                    for item in order.items.all()
                ],
                "total": sum(
                    (item.price_per_item + item.tax_amount) * item.quantity
                    for item in order.items.all()
                ),
                "shipping_method": "pick_up",
                "payment_method": payment_method or "credit_card",
                "notes": "Please leave at front door"
            }
        }, status=status.HTTP_200_OK)  # Optional: explicit 200 OK

    except Order.DoesNotExist:
        return Response({
            "error": f"Order with ID {order_id} not found",
            "code": "order_not_found",
            "detail": f"The requested order #{order_id} does not exist"
        }, status=status.HTTP_404_NOT_FOUND)  # Use status constant instead of 404
