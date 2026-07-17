# cart/serializers.py
from decimal import Decimal
from rest_framework import serializers
from django.apps import apps
from .models import CartItem

class CartItemReadSerializer(serializers.ModelSerializer):
    """
    Serializador de lectura optimizado.
    Contrato estricto: La vista que consuma este serializador DEBE 
    implementar `queryset.select_related('variant__product')` para evitar N+1.
    """
    product_name = serializers.CharField(source='variant.product.name', read_only=True)
    product_slug = serializers.CharField(source='variant.product.slug', read_only=True)
    selling_price = serializers.DecimalField(source='variant.selling_price', max_digits=10, decimal_places=2, read_only=True)
    thumbnail = serializers.URLField(source='variant.thumbnail', read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id', 
            'variant_id', 
            'product_name', 
            'product_slug', 
            'selling_price', 
            'quantity', 
            'thumbnail', 
            'total_price'
        ]

    def get_total_price(self, obj: CartItem) -> Decimal:
        # Mantenemos el cálculo estricto en Decimal para garantizar precisión financiera.
        return obj.quantity * obj.variant.selling_price


class CartActionSerializer(serializers.Serializer):
    """
    Serializador de escritura estricto para mutaciones (POST/PATCH).
    Implementa resolución dinámica para evitar importaciones circulares transversales.
    """
    productvariantid = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate_productvariantid(self, value: int):
        # Lazy loading del modelo. Aísla el dominio de 'cart' del dominio de 'products', 
        # previniendo cuellos de botella e ImportError / AppRegistryNotReady en el StatReloader.
        ProductVariant = apps.get_model('products', 'ProductVariant')
        
        try:
            return ProductVariant.objects.get(pk=value, is_active=True)
        except ProductVariant.DoesNotExist:
            raise serializers.ValidationError("La variante seleccionada no existe o está inactiva.")

    def validate(self, attrs: dict) -> dict:
        variant = attrs['productvariantid']
        quantity = attrs['quantity']

        # Validación de inventario atómica
        if variant.stock < quantity:
            raise serializers.ValidationError({
                "quantity": f"Stock insuficiente. Disponible: {variant.stock}"
            })
            
        return attrs