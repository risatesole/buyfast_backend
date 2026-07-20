from rest_framework.response import Response
from cart.models import CartItem


def checkout_handler_get(request):
    user = request.user

    items = (
        CartItem.objects
        .filter(cart__user=user)
        .select_related("cart", "variant", "variant__product")
    )

    return Response({
        "status": "ok",
        "data": {
            "cart": {
                "items": [
                    {
                        "id": item.id,
                        "variant_id": item.variant.id,
                        "product_name": item.variant.product.name,
                        "variant_name": item.variant.name,
                        "quantity": item.quantity,
                        "selling_price": float(item.variant.selling_price),

                        # Mantengo esta estructura para compatibilidad con tu CheckoutPage actual,
                        # porque tu frontend usa item.product.id, item.product.name, etc.
                        "product": {
                            "id": item.variant.id,
                            "name": item.variant.name,
                            "description": item.variant.description,
                            "selling_price": float(item.variant.selling_price),
                        },

                        # También dejo productvariant por si otra parte del frontend lo usa.
                        "productvariant": {
                            "id": item.variant.id,
                            "name": item.variant.name,
                            "description": item.variant.description,
                            "selling_price": float(item.variant.selling_price),
                        },
                    }
                    for item in items
                ]
            },
            "user": {
                "id": user.id,
                "firstname": getattr(user, "first_name", ""),
                "lastname": getattr(user, "last_name", ""),
                "email": getattr(user, "email", ""),
                "matricula": getattr(user, "matricula", ""),
                "phone_number": getattr(user, "phone_number", ""),
                "permissions": [],
                "profilepicture": getattr(user, "profilepicture", "") or "",
            }
        }
    })