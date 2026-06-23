# orders/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum, Count
from .models import Order, OrderItem, OrderPayment


class OrderItemInline(admin.TabularInline):
    """Inline admin for Order Items"""
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal_display', 'product_link')
    fields = ('product', 'quantity', 'price_per_item', 'tax_amount', 'subtotal_display')
    
    def product_link(self, obj):
        """Create a link to the product in admin"""
        if obj.product:
            url = reverse('admin:products_product_change', args=[obj.product.id])
            return format_html('<a href="{}">{}</a>', url, obj.product.name)
        return "-"
    product_link.short_description = "Product"
    
    def subtotal_display(self, obj):
        """Display subtotal with currency symbol"""
        return f"${obj.subtotal:.2f}" if obj.subtotal else "$0.00"
    subtotal_display.short_description = "Subtotal"


class OrderPaymentInline(admin.StackedInline):
    """Inline admin for Order Payment"""
    model = OrderPayment
    extra = 0
    readonly_fields = ('created_at', 'total_amount_display')
    fields = ('payment_provider', 'payment_provider_transaction', 
              'amount', 'tax_amount', 'total_amount_display', 'created_at')
    
    def total_amount_display(self, obj):
        """Display total amount with currency symbol"""
        total = obj.amount + obj.tax_amount if obj.amount else 0
        return f"${total:.2f}"
    total_amount_display.short_description = "Total Amount"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for Order model"""
    list_display = (
        'id', 
        'customer_email', 
        'status_badge', 
        'pickup_time',
        'total_items_display',
        'total_amount_display',
        'created_at'
    )
    list_filter = (
        'status',
        'created_at',
        'pickup_time',
    )
    search_fields = (
        'id',
        'customer__email',
        'customer__first_name',
        'customer__last_name',
    )
    readonly_fields = ('created_at', 'total_amount_display', 'total_items_display')
    fieldsets = (
        ('Order Information', {
            'fields': ('customer', 'status', 'pickup_time')
        }),
        ('Summary', {
            'fields': ('total_items_display', 'total_amount_display'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    inlines = [OrderItemInline, OrderPaymentInline]
    date_hierarchy = 'created_at'
    actions = ['mark_as_fulfilled', 'mark_as_returned']
    
    def customer_email(self, obj):
        """Display customer email with link to user admin"""
        if obj.customer:
            url = reverse('admin:accounts_user_change', args=[obj.customer.id])
            return format_html('<a href="{}">{}</a>', url, obj.customer.email)
        return "-"
    customer_email.short_description = "Customer"
    customer_email.admin_order_field = 'customer__email'
    
    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'pending': 'orange',
            'fulfilled': 'green',
            'returned': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Status"
    
    def total_items_display(self, obj):
        """Display total number of items in order"""
        total = obj.items.aggregate(total=Sum('quantity'))['total'] or 0
        return f"{total} items"
    total_items_display.short_description = "Total Items"
    
    def total_amount_display(self, obj):
        """Display total order amount"""
        try:
            if hasattr(obj, 'payment') and obj.payment:
                total = obj.payment.amount + obj.payment.tax_amount
                return f"${total:.2f}"
        except:
            pass
        
        # Calculate from items if no payment exists
        total = obj.items.aggregate(
            total=Sum('subtotal')
        )['total'] or 0
        return f"${total:.2f}" if total else "$0.00"
    total_amount_display.short_description = "Total Amount"
    
    def mark_as_fulfilled(self, request, queryset):
        """Action to mark selected orders as fulfilled"""
        updated = queryset.update(status=Order.Status.FULFILLED)
        self.message_user(request, f"{updated} orders marked as fulfilled.")
    mark_as_fulfilled.short_description = "Mark selected orders as fulfilled"
    
    def mark_as_returned(self, request, queryset):
        """Action to mark selected orders as returned"""
        updated = queryset.update(status=Order.Status.RETURNED)
        self.message_user(request, f"{updated} orders marked as returned.")
    mark_as_returned.short_description = "Mark selected orders as returned"
    
    def get_queryset(self, request):
        """Optimize queries with prefetch_related and select_related"""
        return super().get_queryset(request).select_related(
            'customer'
        ).prefetch_related(
            'items',
            'items__product',
            'payment',
            'payment__payment_provider'
        )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin configuration for OrderItem model"""
    list_display = (
        'id',
        'order_link',
        'product_link',
        'quantity',
        'price_per_item',
        'tax_amount',
        'subtotal_display'
    )
    list_filter = (
        'order__status',
        'product__category',
    )
    search_fields = (
        'order__id',
        'product__name',
        'product__sku',
    )
    readonly_fields = ('subtotal_display',)
    fields = ('order', 'product', 'quantity', 'price_per_item', 'tax_amount', 'subtotal_display')
    
    def order_link(self, obj):
        """Link to order admin"""
        if obj.order:
            url = reverse('admin:orders_order_change', args=[obj.order.id])
            return format_html('<a href="{}">Order #{}</a>', url, obj.order.id)
        return "-"
    order_link.short_description = "Order"
    
    def product_link(self, obj):
        """Link to product admin"""
        if obj.product:
            url = reverse('admin:products_product_change', args=[obj.product.id])
            return format_html('<a href="{}">{}</a>', url, obj.product.name)
        return "-"
    product_link.short_description = "Product"
    
    def subtotal_display(self, obj):
        """Display subtotal with currency symbol"""
        return f"${obj.subtotal:.2f}" if obj.subtotal else "$0.00"
    subtotal_display.short_description = "Subtotal"


@admin.register(OrderPayment)
class OrderPaymentAdmin(admin.ModelAdmin):
    """Admin configuration for OrderPayment model"""
    list_display = (
        'id',
        'order_link',
        'payment_provider_name',
        'amount_display',
        'tax_amount_display',
        'total_amount_display',
        'created_at'
    )
    list_filter = (
        'payment_provider',
        'created_at',
    )
    search_fields = (
        'order__id',
        'payment_provider__name',
        'payment_provider_transaction__transaction_id',
    )
    readonly_fields = ('created_at', 'total_amount_display')
    fields = (
        'order',
        'payment_provider',
        'payment_provider_transaction',
        'amount',
        'tax_amount',
        'total_amount_display',
        'created_at'
    )
    
    def order_link(self, obj):
        """Link to order admin"""
        if obj.order:
            url = reverse('admin:orders_order_change', args=[obj.order.id])
            return format_html('<a href="{}">Order #{}</a>', url, obj.order.id)
        return "-"
    order_link.short_description = "Order"
    
    def payment_provider_name(self, obj):
        """Display payment provider name"""
        return obj.payment_provider.name if obj.payment_provider else "-"
    payment_provider_name.short_description = "Provider"
    payment_provider_name.admin_order_field = 'payment_provider__name'
    
    def amount_display(self, obj):
        """Display amount with currency symbol"""
        return f"${obj.amount:.2f}" if obj.amount else "$0.00"
    amount_display.short_description = "Amount"
    
    def tax_amount_display(self, obj):
        """Display tax amount with currency symbol"""
        return f"${obj.tax_amount:.2f}" if obj.tax_amount else "$0.00"
    tax_amount_display.short_description = "Tax"
    
    def total_amount_display(self, obj):
        """Display total amount with currency symbol"""
        total = obj.amount + obj.tax_amount if obj.amount else 0
        return f"${total:.2f}"
    total_amount_display.short_description = "Total Amount"
