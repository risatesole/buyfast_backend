from django.db import models
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager


class Product(models.Model):
    # Tipos de producto reales para un e-commerce
    class ProductType(models.TextChoices):
        PHYSICAL = "physical", _("Físico")
        DIGITAL = "digital", _("Digital")
        SERVICE = "service", _("Servicio")

    # Categorías del economato
    class Category(models.TextChoices):
        STATIONERY = "stationery", _("Papelería y Suministros")
        BOOKS_MANUALS = "books_manuals", _("Libros y Manuales")
        MEDICAL_LAB = "medical_lab", _("Medicina y Laboratorio")
        ARCHITECTURE_ARTS = "architecture_arts", _("Arquitectura y Artes")
        ELECTRONICS = "electronics", _("Electrónica y Calculadoras")
        UNIFORMS = "uniforms", _("Uniformes e Institucional")
        SNACKS_BEVERAGES = "snacks_beverages", _("Snacks y Bebidas")

        @classmethod
        def all(cls):
            return [
                {
                    "slug": category.value,
                    "label": category.label,
                    **cls.INFO[category],
                }
                for category in cls
            ]

        @classmethod
        def get(cls, category):
            return {
                "slug": category.value,
                "label": category.label,
                **cls.INFO[category],
            }

    # Campos de identificación
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    # Clasificación
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        default=Category.STATIONERY,
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


Product.Category.INFO = {
    Product.Category.STATIONERY: {
        "description": _("Cuadernos, bolígrafos, papel y material gastable."),
        "priority": 1,
        "images": {
            "banner": "https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=1200&h=400&fit=crop",
            "cart": "https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=100&h=100&fit=crop",
            "default": "https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=400&h=400&fit=crop",
        },
    },
    Product.Category.BOOKS_MANUALS: {
        "description": _("Textos universitarios, manuales de laboratorio y guías."),
        "priority": 1,
        "images": {
            "banner": "https://images.unsplash.com/photo-150784272343-583f20270319?w=1200&h=400&fit=crop",
            "cart": "https://images.unsplash.com/photo-1507842872343-583f20270319?w=100&h=100&fit=crop",
            "default": "https://images.unsplash.com/photo-1507842872343-583f20270319?w=400&h=400&fit=crop",
        },
    },
    Product.Category.MEDICAL_LAB: {
        "description": _("Estetoscopios, batas médicas, kits de disección y bioseguridad."),
        "priority": 1,
        "images": {
            "banner": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=1200&h=400&fit=crop",
            "cart": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=100&h=100&fit=crop",
            "default": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=400&h=400&fit=crop",
        },
    },
    Product.Category.ARCHITECTURE_ARTS: {
        "description": _("Reglas T, escalímetros, maquetas, pinturas y pinceles."),
        "priority": 2,
        "images": {
            "banner": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=1200&h=400&fit=crop",
            "cart": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=100&h=100&fit=crop",
            "default": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=400&h=400&fit=crop",
        },
    },
    Product.Category.ELECTRONICS: {
        "description": _("Calculadoras científicas, memorias USB y accesorios periféricos."),
        "priority": 2,
        "images": {
            "banner": "https://images.unsplash.com/photo-1550355291-bbee04a92027?w=1200&h=400&fit=crop",
            "cart": "https://images.unsplash.com/photo-1550355291-bbee04a92027?w=100&h=100&fit=crop",
            "default": "https://images.unsplash.com/photo-1550355291-bbee04a92027?w=400&h=400&fit=crop",
        },
    },
    Product.Category.UNIFORMS: {
        "description": _("T-shirts UASD, ropa deportiva y promocionales."),
        "priority": 3,
        "images": {
            "banner": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200&h=400&fit=crop",
            "cart": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=100&h=100&fit=crop",
            "default": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=400&fit=crop",
        },
    },
    Product.Category.SNACKS_BEVERAGES: {
        "description": _("Comida rápida, café, agua y meriendas."),
        "priority": 3,
        "images": {
            "banner": "https://images.unsplash.com/photo-1495521821757-a1efb6729352?w=1200&h=400&fit=crop",
            "cart": "https://images.unsplash.com/photo-1495521821757-a1efb6729352?w=100&h=100&fit=crop",
            "default": "https://images.unsplash.com/photo-1495521821757-a1efb6729352?w=400&h=400&fit=crop",
        },
    },
}
