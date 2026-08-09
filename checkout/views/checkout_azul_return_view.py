from rest_framework.decorators import api_view

from ..handlers.checkout_handler_azul_return import (
    handle_azul_approved,
    handle_azul_cancelled,
    handle_azul_declined,
)


@api_view(["GET"])
def checkout_azul_approved_view(request):
    return handle_azul_approved(request)


@api_view(["GET"])
def checkout_azul_declined_view(request):
    return handle_azul_declined(request)


@api_view(["GET"])
def checkout_azul_cancelled_view(request):
    return handle_azul_cancelled(request)
