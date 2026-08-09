from django.db import transaction
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework import status

from api.utils import CsrfExemptSessionAuthentication
from data_transfer_objects.ErrorResponse import ErrorResponse, ErrorCode
from orders.models import Order, OrderPayment
from orders.orders import cancel_unpaid_order
from payment.models import PaymentProvider, PaymentProviderTransaction
from payment.payment import create_paypal_order, capture_paypal_order, PayPalAPIError
from checkout.handlers.checkout_handler_post import remove_cart_item, send_order_confirmation_email


def _get_own_awaiting_order(request, order_id):
    """
    Looks up an order owned by the requesting user that's still awaiting
    payment. Returns (order, None) on success, or (None, error_response).
    """
    try:
        order = Order.objects.get(id=order_id, customer=request.user)
    except (Order.DoesNotExist, ValueError, TypeError):
        error = ErrorResponse(ErrorCode.RESOURCE_NOT_FOUND, "Order not found", "error", 404)
        return None, error.http_response()

    if order.status != Order.Status.AWAITING_PAYMENT:
        error = ErrorResponse(
            ErrorCode.CONFLICT, "This order is not awaiting payment", "error", 409
        )
        return None, error.http_response()

    return order, None


@api_view(["POST"])
@authentication_classes([CsrfExemptSessionAuthentication])
def paypal_create_order_api_view(request):
    if not request.user.is_authenticated:
        error = ErrorResponse(
            ErrorCode.CHECKOUT_LOGIN_REQUIRED, "user must log in in order to checkout", "error", 400
        )
        return error.http_response()

    order, error_response = _get_own_awaiting_order(request, request.data.get("order_id"))
    if error_response:
        return error_response

    try:
        paypal_order_id = create_paypal_order(order)
    except PayPalAPIError as e:
        error = ErrorResponse(ErrorCode.SERVICE_UNAVAILABLE, f"PayPal error: {e}", "error", 502)
        return error.http_response()

    return Response({"success": True, "paypal_order_id": paypal_order_id}, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([CsrfExemptSessionAuthentication])
def paypal_capture_api_view(request):
    if not request.user.is_authenticated:
        error = ErrorResponse(
            ErrorCode.CHECKOUT_LOGIN_REQUIRED, "user must log in in order to checkout", "error", 400
        )
        return error.http_response()

    order, error_response = _get_own_awaiting_order(request, request.data.get("order_id"))
    if error_response:
        return error_response

    paypal_order_id = request.data.get("paypal_order_id")

    try:
        capture_response = capture_paypal_order(paypal_order_id)
    except PayPalAPIError as e:
        cancel_unpaid_order(order)
        error = ErrorResponse(ErrorCode.SERVICE_UNAVAILABLE, f"PayPal error: {e}", "error", 502)
        return error.http_response()

    if capture_response.get("status") != "COMPLETED":
        cancel_unpaid_order(order)
        return Response(
            {"success": False, "status": "error", "message": "Payment was not completed"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    capture = capture_response["purchase_units"][0]["payments"]["captures"][0]
    amount = sum(item.subtotal for item in order.items.all())
    tax_amount = sum(item.tax_amount * item.quantity for item in order.items.all())

    with transaction.atomic():
        paypal_provider, _ = PaymentProvider.objects.get_or_create(
            name="PayPal",
            defaults={"description": "PayPal Sandbox (demo)"},
        )
        provider_transaction = PaymentProviderTransaction.objects.create(
            payment_provider=paypal_provider,
            reference_document=capture["id"],
            amount=amount,
            tax=tax_amount,
        )
        OrderPayment.objects.create(
            order=order,
            payment_provider=paypal_provider,
            payment_provider_transaction=provider_transaction,
            amount=amount,
            tax_amount=tax_amount,
        )
        order.status = Order.Status.PENDING
        order.save()

    items = [
        {"productvariantid": item.product_id, "quantity": item.quantity}
        for item in order.items.all()
    ]
    remove_cart_item(items, order.customer)
    try:
        send_order_confirmation_email(order)
    except Exception as e:
        print(f"Failed to send order confirmation email for order {order.id}: {e}")

    return Response(
        {"success": True, "order_id": order.id, "status": order.status}, status=status.HTTP_200_OK
    )


@api_view(["POST"])
@authentication_classes([CsrfExemptSessionAuthentication])
def paypal_cancel_api_view(request):
    if not request.user.is_authenticated:
        error = ErrorResponse(
            ErrorCode.CHECKOUT_LOGIN_REQUIRED, "user must log in in order to checkout", "error", 400
        )
        return error.http_response()

    try:
        order = Order.objects.get(id=request.data.get("order_id"), customer=request.user)
    except (Order.DoesNotExist, ValueError, TypeError):
        error = ErrorResponse(ErrorCode.RESOURCE_NOT_FOUND, "Order not found", "error", 404)
        return error.http_response()

    cancel_unpaid_order(order)
    return Response(
        {"success": True, "order_id": order.id, "status": order.status}, status=status.HTTP_200_OK
    )
