from django.db import models
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager

class Product(models.Model):
    # Tipos de producto reales para un e-commerce, separando la naturaleza del artículo de su categorización
    class ProductType(models.TextChoices):
        PHYSICAL = 'physical', _('Físico')
        DIGITAL = 'digital', _('Digital')
        SERVICE = 'service', _('Servicio')

    # Categorías estrictamente alineadas al dominio del economato de la UASD
    class Category(models.TextChoices):
        STATIONERY = 'stationery', _('Papelería y Suministros')
        BOOKS_MANUALS = 'books_manuals', _('Libros y Manuales')
        MEDICAL_LAB = 'medical_lab', _('Medicina y Laboratorio')
        ARCHITECTURE_ARTS = 'architecture_arts', _('Arquitectura y Artes')
        ELECTRONICS = 'electronics', _('Electrónica y Calculadoras')
        UNIFORMS = 'uniforms', _('Uniformes e Institucional')
        SNACKS_BEVERAGES = 'snacks_beverages', _('Snacks y Bebidas')

    # Campos de identificación (optimizados para búsquedas)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    
    # Clasificación
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        default=Category.STATIONERY,
        db_index=True  # Crítico para rendimiento al filtrar productos por categoría en el frontend
    )
    product_type = models.CharField(
        max_length=20,
        choices=ProductType.choices,
        default=ProductType.PHYSICAL
    )
    
    # Media y Metadatos
    thumbnail = models.URLField(max_length=1000, blank=True)
    tags = TaggableManager(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_product"
        ordering = ["-created_at"]
        verbose_name = _("Producto")
        verbose_name_plural = _("Productos")

    def __str__(self) -> str:
        return self.name