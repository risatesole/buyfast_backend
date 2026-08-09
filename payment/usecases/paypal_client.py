import base64
import json
import urllib.error
import urllib.request

from django.conf import settings


class PayPalAPIError(Exception):
    def __init__(self, message="PayPal API request failed"):
        self.message = message
        super().__init__(self.message)


def _request(method, path, headers, body=None):
    url = f"{settings.PAYPAL_API_BASE}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(url, data=data, method=method, headers=headers)

    try:
        with urllib.request.urlopen(request) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise PayPalAPIError(f"PayPal API error ({e.code}): {error_body}") from e


def get_paypal_access_token() -> str:
    credentials = f"{settings.PAYPAL_CLIENT_ID}:{settings.PAYPAL_CLIENT_SECRET}".encode("utf-8")
    basic_auth = base64.b64encode(credentials).decode("utf-8")

    request = urllib.request.Request(
        f"{settings.PAYPAL_API_BASE}/v1/oauth2/token",
        data=b"grant_type=client_credentials",
        method="POST",
        headers={
            "Authorization": f"Basic {basic_auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

    try:
        with urllib.request.urlopen(request) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise PayPalAPIError(f"PayPal OAuth error ({e.code}): {error_body}") from e

    return payload["access_token"]


def create_paypal_order(order) -> str:
    """
    Creates a PayPal order for the given Order's total.

    Charged in USD: PayPal Sandbox doesn't support DOP as a transaction
    currency, so the DOP total is passed through unconverted — a demo/sandbox
    simplification only, not a real currency conversion.

    Returns the PayPal order id.
    """
    access_token = get_paypal_access_token()
    total = sum(item.subtotal for item in order.items.all())

    body = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "reference_id": str(order.id),
                "amount": {
                    "currency_code": "USD",
                    "value": f"{total:.2f}",
                },
            }
        ],
    }

    response = _request(
        "POST",
        "/v2/checkout/orders",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        body=body,
    )
    return response["id"]


def capture_paypal_order(paypal_order_id: str) -> dict:
    """
    Captures a previously-approved PayPal order.

    Returns the raw capture response — callers must check
    response["status"] == "COMPLETED" before treating the payment as
    successful.
    """
    access_token = get_paypal_access_token()

    return _request(
        "POST",
        f"/v2/checkout/orders/{paypal_order_id}/capture",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        body={},
    )
