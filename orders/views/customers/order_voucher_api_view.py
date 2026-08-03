from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from api.utils import CsrfExemptSessionAuthentication
from ...models import Order
from ...voucher_pdf import build_order_voucher_pdf


@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def order_voucher_api_view(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related('customer').prefetch_related('items__product__product'),
        id=order_id,
        customer=request.user,
    )

    pdf_bytes = build_order_voucher_pdf(order)

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="comprobante-pedido-{order.id}.pdf"'
    return response
