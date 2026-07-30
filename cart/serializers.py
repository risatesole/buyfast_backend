from decimal import Decimal

from rest_framework import serializers

from .models import CartItem
from products.default.models import ProductVariant


class CartItemReadSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="variant.product.name", read_only=True)
    product_slug = serializers.CharField(source="variant.product.slug", read_only=True)
    variant_name = serializers.CharField(source="variant.name", read_only=True)

    selling_price = serializers.DecimalField(
        source="variant.selling_price",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    thumbnail = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "variant_id",
            "product_name",
            "variant_name",
            "product_slug",
            "selling_price",
            "quantity",
            "thumbnail",
            "total_price",
        ]

    def get_thumbnail(self, obj):
        thumbnails = getattr(obj.variant, "prefetched_thumbnails", [])

        if not thumbnails:
            return None

        # NOTE: ProductImage.image is a CharField holding a URL string,
        # not a Django ImageField/FileField — it has no `.url` attribute.
        image_url = thumbnails[0].image

        if not image_url:
            return None

        request = self.context.get("request")
        if request and image_url.startswith("/"):
            return request.build_absolute_uri(image_url)

        return image_url

    def get_total_price(self, obj: CartItem) -> Decimal:
        return obj.quantity * obj.variant.selling_price


class CartActionSerializer(serializers.Serializer):
    productvariantid = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate_productvariantid(self, value: int):
        try:
            return ProductVariant.objects.get(pk=value)
        except ProductVariant.DoesNotExist:
            raise serializers.ValidationError(
                "La variante seleccionada no existe."
            )

    def validate(self, attrs: dict) -> dict:
        return attrs
