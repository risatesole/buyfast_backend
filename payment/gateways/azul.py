import hashlib
import hmac

from django.conf import settings
from django.urls import reverse

# Field order and hashing steps are copied verbatim from Azul's own
# "Documento E-Commerce AZUL Página de Pagos" guide (request/response AuthHash
# sections), not guessed — do not reorder without checking that doc again.

REQUEST_HASH_FIELDS = [
    "MerchantId",
    "MerchantName",
    "MerchantType",
    "CurrencyCode",
    "OrderNumber",
    "Amount",
    "ITBIS",
    "ApprovedUrl",
    "DeclinedUrl",
    "CancelUrl",
    "UseCustomField1",
    "CustomField1Label",
    "CustomField1Value",
    "UseCustomField2",
    "CustomField2Label",
    "CustomField2Value",
]

RESPONSE_HASH_FIELDS = [
    "OrderNumber",
    "Amount",
    "AuthorizationCode",
    "DateTime",
    "ResponseCode",
    "IsoCode",
    "ResponseMessage",
    "ErrorDescription",
    "RRN",
]


def _format_money(value: float) -> str:
    """Azul wants digit strings with no decimal separator; last two digits are cents."""
    return str(int(round(value * 100)))


def _compute_hash(concatenated: str) -> str:
    # Message is UTF-16LE per Azul's own C#/PHP reference implementations; the
    # HMAC key itself is used as a plain string, not re-encoded the same way.
    message = concatenated.encode("utf-16-le")
    key = settings.AZUL_AUTH_KEY.encode("utf-8")
    return hmac.new(key, message, hashlib.sha512).hexdigest()


def build_payment_page_fields(order, request) -> dict:
    total = sum(item.subtotal for item in order.items.all())
    tax = sum(item.tax_amount * item.quantity for item in order.items.all())

    fields = {
        "MerchantId": settings.AZUL_MERCHANT_ID,
        "MerchantName": settings.AZUL_MERCHANT_NAME,
        "MerchantType": settings.AZUL_MERCHANT_TYPE,
        "CurrencyCode": settings.AZUL_CURRENCY_CODE,
        "OrderNumber": str(order.id),
        "Amount": _format_money(total),
        "ITBIS": _format_money(tax),
        "ApprovedUrl": request.build_absolute_uri(reverse("api:payment-azul-approved")),
        "DeclinedUrl": request.build_absolute_uri(reverse("api:payment-azul-declined")),
        "CancelUrl": request.build_absolute_uri(reverse("api:payment-azul-cancelled")),
        "UseCustomField1": "0",
        "CustomField1Label": "",
        "CustomField1Value": "",
        "UseCustomField2": "0",
        "CustomField2Label": "",
        "CustomField2Value": "",
        "Locale": "ES",
    }

    hash_input = "".join(fields[name] for name in REQUEST_HASH_FIELDS) + settings.AZUL_AUTH_KEY
    fields["AuthHash"] = _compute_hash(hash_input)

    return {
        "post_url": settings.AZUL_PAYMENT_PAGE_URL,
        "fields": fields,
    }


def verify_response_hash(data) -> bool:
    received_hash = data.get("AuthHash", "")
    hash_input = "".join(data.get(name, "") for name in RESPONSE_HASH_FIELDS) + settings.AZUL_AUTH_KEY
    expected_hash = _compute_hash(hash_input)
    return hmac.compare_digest(expected_hash.lower(), received_hash.lower())
