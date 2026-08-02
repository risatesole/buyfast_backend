from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True, default="")
    priority = models.PositiveIntegerField(default=0)

    image_banner = models.URLField(max_length=1000, blank=True, default="")
    image_cart = models.URLField(max_length=1000, blank=True, default="")
    image_default = models.URLField(max_length=1000, blank=True, default="")

    class Meta:
        db_table = "core_category"
        ordering = ["priority", "name"]
        verbose_name = _("Categoría")
        verbose_name_plural = _("Categorías")

    def __str__(self):
        return self.name

    def as_dict(self):
        return {
            "slug": self.slug,
            "label": self.name,
            "description": self.description,
            "priority": self.priority,
            "images": {
                "banner": self.image_banner,
                "cart": self.image_cart,
                "default": self.image_default,
            },
        }
