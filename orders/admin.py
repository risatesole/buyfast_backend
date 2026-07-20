# orders/admin.py
from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    # Eliminado raw_id_fields para forzar el renderizado de un dropdown (<select>) estándar.
    readonly_fields = ('get_safe_subtotal',)

    @admin.display(description='Subtotal')
    def get_safe_subtotal(self, obj: OrderItem) -> float:
        """
        Intercepta la evaluación de subtotal en formularios vacíos (/add/)
        para evitar el TypeError con valores NoneType.
        """
        if obj.price_per_item is None or obj.quantity is None:
            return 0.0
        return obj.subtotal

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_customer_email', 'status', 'pickup_time', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'customer__email', 'customer__first_name', 'customer__last_name')
    date_hierarchy = 'created_at'
    
    # Mantiene la optimización N+1 para listados
    list_select_related = ('customer',)
    
    inlines = [OrderItemInline]

    @admin.display(description='Customer Email', ordering='customer__email')
    def get_customer_email(self, obj: Order) -> str:
        return obj.customer.email

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_link', 'product', 'quantity', 'price_per_item', 'get_safe_subtotal')
    search_fields = ('order__id', 'product__name', 'product__sku')
    
    list_select_related = ('order', 'product')

    @admin.display(description='Order', ordering='order__id')
    def order_link(self, obj: OrderItem) -> str:
        return f"Order #{obj.order.id}"

    @admin.display(description='Subtotal')
    def get_safe_subtotal(self, obj: OrderItem) -> float:
        if obj.price_per_item is None or obj.quantity is None:
            return 0.0
        return obj.subtotal
