from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from ...utils import CsrfExemptSessionAuthentication 
from .handlers.products_handler_get import products_get_handler_get
from .handlers.products_handler_post import products_get_handler_post

@api_view(['GET', 'POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
def products(request):
    if request.method == 'GET':
        return Response(products_get_handler_get(request))
    
    if request.method == 'POST':
        return products_get_handler_post(request)
