from django.db import ProgrammingError
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response

from api.utils import CsrfExemptSessionAuthentication
from products.models import Product
from ..handlers.checkout_handler_post import checkout_handler_post
from ..handlers.checkout_handler_get import checkout_handler_get
from ..handlers.checkout_handler_delete import checkout_handler_delete

@api_view(["GET", "POST", "DELETE"])
@authentication_classes([CsrfExemptSessionAuthentication])
def checkout_api_view(request):
    try:
        user = request.user

        if not user.is_authenticated:
            return Response({
                "status": "error",
                "message": "Authentication required",
                "data": None,
                "error":{"message":"Authentication required"}
            }, status=401)

        if request.method == "GET":
            return checkout_handler_get(request)

        if request.method == "POST":
            return checkout_handler_post(request)

        if request.method == "DELETE":
            checkout_handler_delete(request)

    except Product.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Product not found"
        }, status=404)

    except ProgrammingError:
        return Response({
            "status": "error",
            "message": (
                "Cart table does not exist. "
                "Run: python manage.py makemigrations cart && python manage.py migrate"
            )
        }, status=500)

    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),
            "data": None
        }, status=400)
