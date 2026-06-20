from django.db import ProgrammingError
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response

from api.utils import CsrfExemptSessionAuthentication
from cart.models import CartItem
from products.models import Product
from accounts.models import User

@api_view(["GET", "POST", "DELETE"])
@authentication_classes([CsrfExemptSessionAuthentication])
def checkout_api_view(request):
    try:
        user = request.user

        if not user.is_authenticated:
            return Response({
                "status": "error",
                "message": "Authentication required",
                "data": None
            }, status=401)

        if request.method == "GET":
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

        if request.method == "POST":
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

            product = Product.objects.get(id=product_id)

            cart_item, created = CartItem.objects.get_or_create(
                user=user,
                product=product,
                defaults={
                    "quantity": quantity
                }
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return Response({
                "status": "ok",
                "message": "Item added to cart",
                "data": {
                    "item": {
                        "id": cart_item.id,
                        "product_id": product.id,
                        "quantity": cart_item.quantity
                    }
                }
            })

        if request.method == "DELETE":
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

    except Product.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Product not found"
        }, status=404)

    except ProgrammingError:
        return Response({
            "status": "error",
            "message": (
                "Cart table does not exist. "
                "Run: python manage.py makemigrations cart && python manage.py migrate"
            )
        }, status=500)

    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),
            "data": None
        }, status=400)
