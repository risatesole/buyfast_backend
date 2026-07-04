from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from ...models import Order
from products.models import ProductImage  # Import ProductImage model


# WAENING : mock
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def orders_api_view(request, order_id):
    try:
        order = Order.objects.select_related(
            'customer',
            'payment__payment_provider',
            'payment__payment_provider_transaction'
        ).prefetch_related(
            'items__product',
            'items__product__images'  # Prefetch product images
        ).get(id=order_id)

        # Calculate total from actual order items
        total = sum(item.subtotal for item in order.items.all())

        # Build items list from actual data
        items = []
        for item in order.items.all():
            # Get hero image for the product
            hero_image = item.product.images.filter(image_type='HERO').first()
            image_url = hero_image.image if hero_image else None

            items.append({
                "id": item.id,
                "product_id": item.product.id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "price": float(item.price_per_item),  # Convert Decimal to float if needed
                "image_url": image_url,
                "sku": getattr(item.product, 'sku', None),  # You may need to add sku field to Product
                "brand": item.product.brand,  # Added brand since you have it
            })

        # Get payment method from actual payment data
        payment_method = None
        if hasattr(order, 'payment'):
            payment_method = order.payment.payment_provider.name

        return Response({
            "data": {
                "id": order.id,
                "profilepicture": order.customer.profile_picture,
                "firstname": order.customer.first_name,
                "lastname": order.customer.last_name,
                "email": order.customer.email,
                "created_at": order.created_at,
                "total": float(total),  # Convert Decimal to float if needed
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
                "items": items,
                "shipping_method": "standard_shipping",  # You might want to add this to Order model
                "payment_method": payment_method or "credit_card",
                "notes": "Please leave at front door"  # You might want to add this to Order model
            }
        })

    except Order.DoesNotExist:
        return Response({
            "error": f"Order with ID {order_id} not found"
        }, status=404)
