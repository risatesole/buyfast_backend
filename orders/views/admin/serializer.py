# orders/views/admin/serializer.py
from rest_framework import serializers
from orders.models import Order 

class OrderListSerializer(serializers.ModelSerializer):
    """
    Serializador administrativo.
    Se restaura su definición para solucionar el ImportError, ya que el archivo 
    había sido sobreescrito por los serializadores de la aplicación 'cart'.
    """
    class Meta:
        model = Order
        fields = '__all__'
        # Implementar prefetch_related/select_related en la vista que consuma esto
        # ej: queryset = Order.objects.select_related('user').prefetch_related('items')