# cart/models.py
from django.db import models
from django.conf import settings

# ELIMINADO: from products.models import ProductVariant 
# Importar modelos directamente de otras apps a nivel de módulo es un anti-patrón 
# en Django que genera ModuleNotFoundError o AppRegistryNotReady durante la inicialización.

class Cart(models.Model):
    """
    Representación del carrito a nivel de base de datos.
    Relación 1:1 con el usuario.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cart_carts'
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self) -> str:
        return f"Cart(user_id={self.user_id})"


class CartItem(models.Model):
    """
    Entidad puente optimizada para el detalle del carrito.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    # RESOLUCIÓN: Uso de evaluación perezosa (Lazy Evaluation) mediante un string.
    # El formato debe ser estrictamente 'nombre_de_la_app.NombreDelModelo'.
    # Si tu app de productos se llama 'catalog' o 'store', ajusta 'products.ProductVariant' a 'catalog.ProductVariant'.
    variant = models.ForeignKey(
        'products.ProductVariant', 
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cart_cart_items'
        unique_together = ('cart', 'variant')
        indexes = [
            models.Index(fields=['cart', 'variant']),
        ]

    def __str__(self) -> str:
        return f"CartItem(cart_id={self.cart_id}, variant_id={self.variant_id}, qty={self.quantity})"