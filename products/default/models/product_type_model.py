from django.db import models

class ProductType(models.Model):
    name = models.CharField(max_length=500)
    description = models.TextField()
    slug = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
