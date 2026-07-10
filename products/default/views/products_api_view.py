from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny

class ProductDetailView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, pk=None):
        """GET /api/products/<id>/"""
        if pk:
            return Response({'id': pk, 'name': 'Product Name'})
        else:
            return Response({'products': ["all"]})

    def post(self, request, pk=None):
        """POST /api/products/"""
        return Response({'message': 'Created'}, status=status.HTTP_201_CREATED)

    def patch(self, request, pk=None):
        """PATCH /api/products/<id>/"""
        return Response({'message': 'Updated'})
