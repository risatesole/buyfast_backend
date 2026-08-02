from django.db import models
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager

from .product_category_model import Category


class Product(models.Model):
    # Tipos de producto reales para un e-commerce
    class ProductType(models.TextChoices):
        PHYSICAL = "physical", _("Físico")
        DIGITAL = "digital", _("Digital")
        SERVICE = "service", _("Servicio")

    # Campos de identificación
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    # Clasificación
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        db_index=True,
    )

    product_type = models.CharField(
        max_length=20,
        choices=ProductType.choices,
        default=ProductType.PHYSICAL,
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

    def __str__(self):
        return self.name
