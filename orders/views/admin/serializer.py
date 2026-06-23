# orders/views/orders_api_serializer.py
from rest_framework import serializers
from accounts.models import User
from orders.models import Order, OrderItem, OrderPayment


class CustomerBasicSerializer(serializers.ModelSerializer):
    """Basic customer info for order listing"""
    full_name = serializers.SerializerMethodField()
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
    
    class Meta:
        model = User
        fields = ["id", "email", "full_name", "first_name", "last_name"]


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name")
    product_sku = serializers.CharField(source="product.sku", default=None)
    subtotal = serializers.FloatField(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "quantity",
            "price_per_item",
            "tax_amount",
            "subtotal"
        ]


class OrderPaymentSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source="payment_provider.name")
    transaction_id = serializers.CharField(source="payment_provider_transaction.transaction_id")
    
    class Meta:
        model = OrderPayment
        fields = [
            "id",
            "provider_name",
            "transaction_id",
            "amount",
            "tax_amount",
            "created_at"
        ]


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer matching the Mockoon format for order listing"""
    
    # Mockoon format fields
    profilepicture = serializers.SerializerMethodField()
    firstname = serializers.CharField(source="customer.first_name")
    lastname = serializers.CharField(source="customer.last_name")
    email = serializers.CharField(source="customer.email")
    total = serializers.SerializerMethodField()
    
    def get_profilepicture(self, obj):
        # Generate a consistent avatar URL based on customer ID
        if obj.customer and obj.customer.id:
            seed = obj.customer.id
            return f"https://api.dicebear.com/9.x/personas/svg?seed={seed}"
        return None
    
    def get_total(self, obj):
        # Calculate total from order items
        total = 0
        if hasattr(obj, 'items'):
            for item in obj.items.all():
                total += (item.price_per_item + item.tax_amount) * item.quantity
        return round(total, 2)
    
    class Meta:
        model = Order
        fields = [
            "id",
            "profilepicture",
            "firstname",
            "lastname",
            "email",
            "created_at",
            "total",
            "pickup_time",
            "status",
        ]
