from rest_framework.response import Response
from cart.cart import CartItem

def checkout_handler_delete(request):
    user = request.user
    product_id = request.data.get("product_id")
    quantity = int(request.data.get("quantity", 1))

    if not product_id:
        return Response({
            "status": "error",
            "message": "product_id is required"
        }, status=400)

    if quantity < 1:
        return Response({
            "status": "error",
            "message": "quantity must be greater than 0"
        }, status=400)

    try:
        cart_item = CartItem.objects.get(
            user=user,
            product_id=product_id
        )
    except CartItem.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Item not found in cart"
        }, status=404)

    cart_item.quantity -= quantity

    if cart_item.quantity <= 0:
        cart_item.delete()

        return Response({
            "status": "ok",
            "message": "Item removed from cart",
            "data": {
                "product_id": int(product_id),
                "quantity": 0
            }
        })

    cart_item.save()

    return Response({
        "status": "ok",
        "message": "Item quantity updated",
        "data": {
            "product_id": int(product_id),
            "quantity": cart_item.quantity
        }
    })
