from django.db import ProgrammingError
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status

from api.utils import CsrfExemptSessionAuthentication
from cart.models import CartItem
from products.models import Product
from accounts.models import User
from ..handlers.checkout_handler_post import checkout_handler_post
from ..handlers.checkout_handler_get import checkout_handler_get

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
            return checkout_handler_get(request)

        if request.method == "POST":
            return checkout_handler_post(request)

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
