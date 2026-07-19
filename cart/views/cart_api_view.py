# cart/views/cart_api_view.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Prefetch

from api.utils import CsrfExemptSessionAuthentication
from cart.models import Cart, CartItem
from products.default.models import ProductVariant, ProductImage
from cart.serializers import CartItemReadSerializer, CartActionSerializer


class CartAPIView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Obtiene los items del carrito del usuario autenticado.
        """

        thumbnail_prefetch = Prefetch(
            "variant__images",
            queryset=ProductImage.objects.filter(
                image_type=ProductImage.ImageType.THUMBNAIL
            ),
            to_attr="prefetched_thumbnails"
        )

        return CartItem.objects.filter(
            cart__user=self.request.user
        ).select_related(
            "cart",
            "variant",
            "variant__product"
        ).prefetch_related(
            thumbnail_prefetch
        )

    def get(self, request):
        items = self.get_queryset()
        serializer = CartItemReadSerializer(items, many=True)

        return Response({
            "status": "ok",
            "data": {
                "items": serializer.data
            }
        })

    def post(self, request):
        serializer = CartActionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "status": "error",
                "message": "Datos inválidos",
                "errors": serializer.errors
            }, status=400)

        data = serializer.validated_data

        variant = data["productvariantid"]
        quantity = data["quantity"]

        if isinstance(variant, int):
            try:
                variant = ProductVariant.objects.get(id=variant)
            except ProductVariant.DoesNotExist:
                return Response({
                    "status": "error",
                    "message": "El producto no existe"
                }, status=404)

        cart, _ = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={
                "quantity": quantity
            }
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save(update_fields=["quantity"])

        return Response({
            "status": "ok",
            "message": "Producto agregado al carrito",
            "data": {
                "item": {
                    "id": cart_item.id,
                    "productvariantid": variant.id,
                    "quantity": cart_item.quantity
                }
            }
        })

    def patch(self, request):
        serializer = CartActionSerializer(data=request.data)

        if not serializer.is_valid() or "quantity" not in request.data:
            return Response({
                "status": "error",
                "message": "quantity y productvariantid son requeridos",
                "errors": serializer.errors
            }, status=400)

        data = serializer.validated_data

        variant = data["productvariantid"]
        quantity = data["quantity"]

        variant_id = variant.id if hasattr(variant, "id") else variant

        try:
            cart_item = CartItem.objects.get(
                cart__user=request.user,
                variant_id=variant_id
            )
        except CartItem.DoesNotExist:
            return Response({
                "status": "error",
                "message": "El producto no está en el carrito"
            }, status=404)

        cart_item.quantity = quantity
        cart_item.save(update_fields=["quantity"])

        return Response({
            "status": "ok",
            "message": "Cantidad actualizada",
            "data": {
                "productvariantid": variant_id,
                "quantity": cart_item.quantity
            }
        })

    def delete(self, request):
        serializer = CartActionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "status": "error",
                "message": "Datos inválidos",
                "errors": serializer.errors
            }, status=400)

        data = serializer.validated_data

        variant = data["productvariantid"]
        quantity = data["quantity"]

        variant_id = variant.id if hasattr(variant, "id") else variant

        try:
            cart_item = CartItem.objects.get(
                cart__user=request.user,
                variant_id=variant_id
            )
        except CartItem.DoesNotExist:
            return Response({
                "status": "error",
                "message": "El producto no está en el carrito"
            }, status=404)

        cart_item.quantity -= quantity

        if cart_item.quantity <= 0:
            cart_item.delete()

            return Response({
                "status": "ok",
                "message": "Producto eliminado del carrito",
                "data": {
                    "productvariantid": variant_id,
                    "quantity": 0
                }
            })

        cart_item.save(update_fields=["quantity"])

        return Response({
            "status": "ok",
            "message": "Cantidad actualizada",
            "data": {
                "productvariantid": variant_id,
                "quantity": cart_item.quantity
            }
        })