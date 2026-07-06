from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from api.utils import CsrfExemptSessionAuthentication 
from ..handlers.products_handler_get import products_get_handler_get
from ..handlers.products_handler_post import products_post_handler

from ..handlers.products_patch_handler import products_patch_handler
from ..products import ProductService

@api_view(['GET', 'POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
def products(request):
    if request.method == 'GET':
        return Response(products_get_handler_get(request))
    
    if request.method == 'POST':
        return products_post_handler(request)


@api_view(['GET', 'PATCH'])
@authentication_classes([CsrfExemptSessionAuthentication])
def product_detail(request, product_id):
    if request.method == 'GET':
        service = ProductService()
        product = service.getProductDetails(product_id)

        if product is None:
            return Response({"status": "error", "message": "Product not found"}, status=404)

        return Response({"status": "ok", "data": product})

    if request.method == 'PATCH':
        return products_patch_handler(request, product_id)
    