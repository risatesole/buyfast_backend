# cart/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Prefetch

from api.utils import CsrfExemptSessionAuthentication
from cart.models import CartItem
from products.default.models import ProductVariant, ProductImage
from cart.serializers import CartItemReadSerializer, CartActionSerializer


class CartAPIView(APIView):
    """
    Refactorización a Class-Based View (CBV) para segregar la lógica HTTP.
    Manejo estricto de autenticación a nivel de clase.
    """
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Aislamiento de la lógica de consulta base resolviendo el problema N+1.
        """
        # Limita el query de imágenes estrictamente a los Thumbnails y los inyecta en un atributo virtual
        thumbnail_prefetch = Prefetch(
            "product_variant__images",
            queryset=ProductImage.objects.filter(image_type=ProductImage.ImageType.THUMBNAIL),
            to_attr="prefetched_thumbnails"
        )
        
        return CartItem.objects.filter(user=self.request.user).select_related(
            "product_variant"
        ).prefetch_related(thumbnail_prefetch)

    def get(self, request):
        items = self.get_queryset()
        serializer = CartItemReadSerializer(items, many=True)
        return Response({"status": "ok", "data": {"items": serializer.data}})

    def post(self, request):
        serializer = CartActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"status": "error", "message": "Invalid data", "errors": serializer.errors}, status=400)
        
        data = serializer.validated_data

        try:
            # Optimizamos recuperando solo el ID para validar existencia, si no se necesita el objeto completo
            variant = ProductVariant.objects.only('id').get(id=data["productvariantid"])
        except ProductVariant.DoesNotExist:
            return Response({"status": "error", "message": "Product not found"}, status=404)

        cart_item, created = CartItem.objects.get_or_create(
            user=request.user, 
            product_variant=variant, 
            defaults={"quantity": data["quantity"]}
        )

        if not created:
            cart_item.quantity += data["quantity"]
            # update_fields optimiza el bloqueo a nivel de base de datos y reduce I/O
            cart_item.save(update_fields=["quantity"])

        return Response({
            "status": "ok",
            "message": "Item added to cart",
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
        # Se exige cantidad estrictamente para PATCH
        if not serializer.is_valid() or "quantity" not in request.data:
            return Response({"status": "error", "message": "quantity and productvariantid are required"}, status=400)
        
        data = serializer.validated_data

        try:
            cart_item = CartItem.objects.get(user=request.user, product_variant_id=data["productvariantid"])
        except CartItem.DoesNotExist:
            return Response({"status": "error", "message": "Item not found in cart"}, status=404)

        cart_item.quantity = data["quantity"]
        cart_item.save(update_fields=["quantity"])

        return Response({
            "status": "ok",
            "message": "Item quantity updated",
            "data": {"productvariantid": data["productvariantid"], "quantity": cart_item.quantity}
        })

    def delete(self, request):
        serializer = CartActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"status": "error", "message": "Invalid data", "errors": serializer.errors}, status=400)
        
        data = serializer.validated_data

        try:
            cart_item = CartItem.objects.get(user=request.user, product_variant_id=data["productvariantid"])
        except CartItem.DoesNotExist:
            return Response({"status": "error", "message": "Item not found in cart"}, status=404)

        cart_item.quantity -= data["quantity"]

        if cart_item.quantity <= 0:
            cart_item.delete()
            return Response({
                "status": "ok",
                "message": "Item removed from cart",
                "data": {"product_id": data["productvariantid"], "quantity": 0}
            })

        cart_item.save(update_fields=["quantity"])
        return Response({
            "status": "ok",
            "message": "Item quantity updated",
            "data": {"product_id": data["productvariantid"], "quantity": cart_item.quantity}
        })