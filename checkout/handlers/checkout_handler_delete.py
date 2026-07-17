# checkout/handlers/checkout_handler_delete.py
from django.db import transaction
from rest_framework import status, serializers
from rest_framework.request import Request
from rest_framework.response import Response

# Importación absoluta desde la capa de modelos correcta (soluciona el ModuleNotFoundError)
from cart.models import CartItem

class CartItemDeleteSerializer(serializers.Serializer):
    """
    Delegamos la validación de tipos y reglas de negocio (min_value) a DRF 
    para mantener el handler limpio y estandarizado.
    """
    product_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(min_value=1, default=1)

@transaction.atomic
def checkout_handler_delete(request: Request) -> Response:
    serializer = CartItemDeleteSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            "status": "error",
            "message": "Invalid data",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    product_id = serializer.validated_data['product_id']
    quantity = serializer.validated_data['quantity']

    try:
        # select_for_update() bloquea la fila a nivel de base de datos durante 
        # la transacción para prevenir 'Lost Updates' en peticiones concurrentes.
        cart_item = CartItem.objects.select_for_update().get(
            user=request.user,
            product_id=product_id
        )
    except CartItem.DoesNotExist:
        return Response(
            {"status": "error", "message": "Item not found in cart"}, 
            status=status.HTTP_404_NOT_FOUND
        )

    cart_item.quantity -= quantity

    if cart_item.quantity <= 0:
        cart_item.delete()
        final_quantity = 0
        message = "Item removed from cart"
    else:
        # update_fields optimiza el query de SQL limitando la escritura solo a la columna mutada
        cart_item.save(update_fields=['quantity'])
        final_quantity = cart_item.quantity
        message = "Item quantity updated"

    return Response({
        "status": "ok",
        "message": message,
        "data": {
            "product_id": product_id,
            "quantity": final_quantity
        }
    }, status=status.HTTP_200_OK)