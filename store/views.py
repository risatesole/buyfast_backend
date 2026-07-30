# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import CarouselSlide
from .serializers import CarouselSlideSerializer

@api_view(['GET'])
def store_carrousel_view(request):
    # Get all active slides, ordered by order field
    slides = CarouselSlide.objects.filter(is_active=True)
    serializer = CarouselSlideSerializer(slides, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
