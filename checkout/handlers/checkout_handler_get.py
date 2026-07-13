from rest_framework.response import Response
from cart.models import CartItem

def checkout_handler_get(request):
    user = request.user
    
    items = CartItem.objects.filter(user=request.user).select_related("product_variant")

    return Response({
        "status": "ok",
        "data": {
            "cart": {
                "items": [
                    {
                        "id": item.id,
                        "productvariant": {
                            "id": item.product_variant.id,
                            "name": item.product_variant.name,
                            "description": item.product_variant.description,
                            "selling_price": item.product_variant.selling_price
                        },
                        "quantity": item.quantity,
                    }
                    for item in items
                ]
            },
            "user": {
                "id": user.id,
                "firstname": user.first_name,   
                "lastname": user.last_name,
                "email": user.email,
                "matricula": user.matricula,
                "phone_number": user.phone_number,
                "permissions": [],
                "profilepicture": ""

            }
        }
    })
