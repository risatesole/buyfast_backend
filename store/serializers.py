from rest_framework import serializers
from .models import CarouselSlide

class CarouselSlideSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarouselSlide
        fields = ['id', 'image', 'title', 'description', 'button_text', 'button_link']
        # If you want to include all fields:
        # fields = '__all__'
    
    # Rename fields to match frontend expectations (if needed)
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Rename button_text to buttonText for frontend
        data['buttonText'] = data.pop('button_text')
        data['buttonLink'] = data.pop('button_link')
        return data
