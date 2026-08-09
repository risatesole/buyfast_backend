from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseRedirect

from orders.models import Order, OrderPayment
from payment.gateways.azul import verify_response_hash
from payment.models import PaymentProvider, PaymentProviderTransaction

from .checkout_handler_post import remove_cart_item, send_order_confirmation_email
from inventory.inventory import sell_products


def _redirect_to_result(order_id, outcome):
    return HttpResponseRedirect(
        f"{settings.FRONTEND_URL}/checkout/result?order={order_id}&status={outcome}"
    )


def _mark_paid(order, data):
    provider = PaymentProvider.objects.filter(is_default=True).first()
    amount = int(data.get("Amount", "0") or 0) / 100
    tax = int(data.get("ITBIS", "0") or 0) / 100

    transaction = PaymentProviderTransaction.objects.create(
        payment_provider=provider,
        reference_document=data.get("AzulOrderId") or data.get("RRN", ""),
        amount=amount,
        tax=tax,
    )
    OrderPayment.objects.create(
        order=order,
        payment_provider=provider,
        payment_provider_transaction=transaction,
        amount=amount,
        tax_amount=tax,
    )

    items = [
        {"productvariantid": item.product_id, "quantity": item.quantity}
        for item in order.items.all()
    ]
    sell_products(items, f"{order.customer} bought the product")
    remove_cart_item(items, order.customer)
    send_order_confirmation_email(order)

    order.status = Order.Status.PENDING
    order.save(update_fields=["status"])


def _mark_failed(order):
    order.status = Order.Status.PAYMENT_FAILED
    order.save(update_fields=["status"])


def _get_order(data):
    order_id = data.get("OrderNumber")
    if not order_id:
        return None
    return Order.objects.filter(id=order_id).first()


def handle_azul_approved(request):
    return _handle_return(request, expect_approved=True)


def handle_azul_declined(request):
    return _handle_return(request, expect_approved=False)


def handle_azul_cancelled(request):
    order = _get_order(request.GET)
    if not order:
        return HttpResponseBadRequest("Unknown order")

    if order.status == Order.Status.AWAITING_PAYMENT:
        _mark_failed(order)

    return _redirect_to_result(order.id, "cancelled")


def _handle_return(request, expect_approved):
    data = request.GET
    order = _get_order(data)
    if not order:
        return HttpResponseBadRequest("Unknown order")

    if order.status != Order.Status.AWAITING_PAYMENT:
        # Already processed — Azul redirected twice, or the customer refreshed
        # the return page. Report the outcome we already recorded.
        already = "approved" if order.status == Order.Status.PENDING else "declined"
        return _redirect_to_result(order.id, already)

    if not verify_response_hash(data):
        return HttpResponseBadRequest("Invalid signature")

    approved = expect_approved and data.get("IsoCode") == "00"

    if approved:
        _mark_paid(order, data)
        return _redirect_to_result(order.id, "approved")

    _mark_failed(order)
    return _redirect_to_result(order.id, "declined")
