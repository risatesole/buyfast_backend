from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework import status
from ...models import Order, OrderItem
from django.core.mail import send_mail

def send_order_fulfilled_email(order):
    send_mail(
        subject=f"Confirmación de entrega del pedido #{order.id}",
        message=(
            f"Estimado(a) {order.customer.first_name} {order.customer.last_name},\n\n"
            "Le confirmamos que su pedido ha sido entregado exitosamente en el Economato UASD.\n\n"
            f"Número de pedido: {order.id}\n"
            f"Fecha y hora de retiro: {order.pickup_time}\n\n"
            "Esperamos que los productos recibidos sean de su satisfacción.\n\n"
            "Si tiene alguna duda, observa algún inconveniente con su pedido o necesita asistencia, puede comunicarse con el personal del Economato UASD.\n\n"
            "Agradecemos su confianza y esperamos atenderle nuevamente.\n\n"
            "Atentamente,\n"
            "Equipo del Economato UASD"
        ),
        from_email=None,
        recipient_list=[order.customer.email],
        fail_silently=False,
    )


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def order_details_admin_view(request, pk):
    try:
        # Validate user permissions
        if not request.user.is_authenticated:
            raise PermissionDenied("Authentication required")

        if not request.user.is_active:
            raise PermissionDenied("Your account is inactive")

        if request.user.role != "employee":
            raise PermissionDenied("Only employees are allowed to perform this action")

        # Get the order
        order = get_object_or_404(Order, pk=pk)

        # Handle GET request - Retrieve order details
        if request.method == 'GET':
            # Serialize order items
            items = []
            for item in order.items.all():
                # Get product images
                images = []
                for img in item.product.images.all():
                    images.append({
                        "id": img.id,
                        "url": img.image,
                        "type": img.image_type,
                        "alt_text": img.alt_text,
                        "order": img.order
                    })
                
                items.append({
                    "id": item.id,
                    "product": {
                        "id": item.product.product.id,
                        "name": item.product.product.name,
                        "variant_id": item.product.id,
                        "variant_name": item.product.name,
                        "sku": item.product.sku,
                        "selling_price": float(item.product.selling_price),
                        "tax_rate": float(item.product.tax_rate),
                        "images": images
                    },
                    "quantity": item.quantity,
                    "price_per_item": item.price_per_item,
                    "tax_amount": item.tax_amount,
                    "subtotal": item.subtotal
                })
            
            order_data = {
                "id": order.id,
                "customer_email": order.customer.email,
                "status": order.status,
                "pickup_time": order.pickup_time,
                "created_at": order.created_at,
                "items": items,
                "total_items": sum(item["quantity"] for item in items)
            }
            
            return Response(
                {"status": "ok", "data": order_data},
                status=status.HTTP_200_OK
            )
        
        # Handle POST request - Mark order as fulfilled
        elif request.method == 'POST':

            if order.status == Order.Status.FULFILLED:
                    return Response(
                        {
                            "status": "error",
                            "message": "Esta orden ya fue marcada como completada."
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

            order.status = Order.Status.FULFILLED
            order.save()
            send_order_fulfilled_email(order)
            
            return Response(
                {
                    "order_id": order.id,
                    "new_status": order.status
                },
                status=status.HTTP_200_OK
            )

    except PermissionDenied as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_403_FORBIDDEN
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(
            {'error': f'Error processing request: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
