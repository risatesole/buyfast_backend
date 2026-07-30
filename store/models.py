# models.py
from django.db import models

class CarouselSlide(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    image = models.URLField(max_length=500, help_text="URL of the carousel image")
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    button_text = models.CharField(max_length=50, help_text="Text displayed on the button")
    button_link = models.CharField(max_length=200, help_text="URL the button links to")
    
    # Optional fields for better management
    order = models.PositiveIntegerField(default=0, help_text="Order in which slides appear")
    is_active = models.BooleanField(default=True, help_text="Show/hide this slide")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Carousel Slide"
        verbose_name_plural = "Carousel Slides"
    
    def __str__(self):
        return f"{self.title} (Slide {self.id})"
