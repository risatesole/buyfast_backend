from rest_framework.response import Response
from cart.models import CartItem

def checkout_handler_get(request):
    user = request.user
    
    items = CartItem.objects.filter(user=user).select_related(
        "product", "product__category"
    ).prefetch_related("product__images", "product__tags")

    return Response({
        "status": "ok",
        "data": {
            "cart": {
                "items": [
                    {
                        "id": item.id,
                        "product": {
                            "id": item.product.id,
                            "name": item.product.name,
                            "description": item.product.description,
                            "brand": item.product.brand,
                            "selling_price": item.product.selling_price,
                            "status": item.product.status,
                            "category": {
                                "id": item.product.category.id,
                                "name": item.product.category.name,
                                "slug": item.product.category.slug,
                                "image": item.product.category.image,
                                "status": item.product.category.status,
                            },
                            "images": [
                                {
                                    "url": image.image,
                                    "type": image.image_type,
                                }
                                for image in item.product.images.all()
                            ],
                            "tags": [
                                tag.name
                                for tag in item.product.tags.all()
                            ],
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
