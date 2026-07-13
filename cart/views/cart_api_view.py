from django.db import ProgrammingError
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response

from api.utils import CsrfExemptSessionAuthentication
from cart.models import CartItem
from products.default.models import ProductVariant


@api_view(["GET", "POST", "PATCH", "DELETE"])
@authentication_classes([CsrfExemptSessionAuthentication])
def cart_api_view(request):
    try:
        user = request.user

        if not user.is_authenticated:
            return Response(
                {"status": "error", "message": "Authentication required", "data": None},
                status=401,
            )

        if request.method == "GET":
            items = CartItem.objects.filter(user=user)

            return Response(
                {
                    "status": "ok",
                    "data": {
                        "items": [
                            {
                                "id": item.id,
                                "product": {
                                    "id": item.product_variant.id,
                                    "name": item.product_variant.name,
                                    "description": item.product_variant.description,
                                    "selling_price": item.product_variant.selling_price,
                                    "slug": item.product_variant.slug,
                                    "tax_rate": item.product_variant.tax_rate,
                                },
                                "quantity": item.quantity,
                            }
                            for item in items
                        ]
                    },
                }
            )

        if request.method == "POST":
            product_variant_id = request.data.get("productvariantid")
            quantity = int(request.data.get("quantity", 1))

            if not product_variant_id:
                return Response(
                    {"status": "error", "message": "productvariantid is required"}, status=400
                )

            if quantity < 1:
                return Response(
                    {"status": "error", "message": "quantity must be greater than 0"},
                    status=400,
                )

            try:
                product_variant = ProductVariant.objects.get(id=int(product_variant_id))
            except ProductVariant.DoesNotExist:
                return Response(
                    {"status": "error", "message": "Product not found"}, status=404
                )

            cart_item, created = CartItem.objects.get_or_create(
                user=user, product_variant=product_variant, defaults={"quantity": quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return Response(
                {
                    "status": "ok",
                    "message": "Item added to cart",
                    "data": {
                        "item": {
                            "id": cart_item.id,
                            "productvariantid": product_variant.id,
                            "quantity": cart_item.quantity,
                        }
                    },
                }
            )

        if request.method == "PATCH":
            product_variant_id = request.data.get("productvariantid")
            quantity = request.data.get("quantity")

            if not product_variant_id:
                return Response(
                    {"status": "error", "message": "productvariantid is required"}, status=400
                )

            if quantity is None:
                return Response(
                    {"status": "error", "message": "quantity is required"}, status=400
                )

            try:
                product_variant_id = int(product_variant_id)
            except (ValueError, TypeError):
                return Response(
                    {"status": "error", "message": "productvariantid must be a valid integer"},
                    status=400,
                )

            try:
                quantity = int(quantity)
            except (ValueError, TypeError):
                return Response(
                    {"status": "error", "message": "quantity must be a valid integer"},
                    status=400,
                )

            if quantity < 1:
                return Response(
                    {"status": "error", "message": "quantity must be greater than 0"},
                    status=400,
                )

            try:
                cart_item = CartItem.objects.get(user=user, product_id=product_variant_id)
            except CartItem.DoesNotExist:
                return Response(
                    {"status": "error", "message": "Item not found in cart"}, status=404
                )

            cart_item.quantity = quantity
            cart_item.save()

            return Response(
                {
                    "status": "ok",
                    "message": "Item quantity updated",
                    "data": {
                        "productvariantid": product_variant_id,
                        "quantity": cart_item.quantity,
                    },
                }
            )

        if request.method == "DELETE":
            product_variant_id = request.data.get("productvariantid")

            if not product_variant_id:
                return Response(
                    {"status": "error", "message": "product_id is required"}, status=400
                )

            try:
                product_variant_id = int(product_variant_id)
            except (ValueError, TypeError):
                return Response(
                    {"status": "error", "message": "productvariantid must be a valid integer"},
                    status=400,
                )

            quantity = request.data.get("quantity", 1)
            try:
                quantity = int(quantity)
            except (ValueError, TypeError):
                return Response(
                    {"status": "error", "message": "quantity must be a valid integer"},
                    status=400,
                )

            if quantity < 1:
                return Response(
                    {"status": "error", "message": "quantity must be greater than 0"},
                    status=400,
                )

            try:

                cart_item = CartItem.objects.get(user=user, product_variant=product_variant_id)
            except CartItem.DoesNotExist:
                return Response(
                    {"status": "error", "message": "Item not found in cart"}, status=404
                )

            cart_item.quantity -= quantity

            if cart_item.quantity <= 0:
                cart_item.delete()

                return Response(
                    {
                        "status": "ok",
                        "message": "Item removed from cart",
                        "data": {"product_id": product_variant_id, "quantity": 0},
                    }
                )

            cart_item.save()

            return Response(
                {
                    "status": "ok",
                    "message": "Item quantity updated",
                    "data": {
                        "product_id": product_variant_id,
                        "quantity": cart_item.quantity,
                    },
                }
            )

    except ProgrammingError:
        return Response(
            {
                "status": "error",
                "message": (
                    "Cart table does not exist. "
                    "Run: python manage.py makemigrations cart && python manage.py migrate"
                ),
            },
            status=500,
        )

    except Exception as e:
        return Response(
            {"status": "error", "message": str(e), "data": None}, status=400
        )