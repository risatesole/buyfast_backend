import uuid
from payment.models import PaymentProvider, PaymentProviderTransaction


class PaymentDeclinedException(Exception):
    def __init__(self, message="Payment declined"):
        self.message = message
        super().__init__(self.message)


def process_payment(
    card_number: str,
    expiry_month: int,
    expiry_year: int,
    cvv: str,
    amount: float,
    tax_amount: float = 0,
    items: list = [],
    cardholder_name: str = "",
    billing_address: dict = {},
) -> PaymentProviderTransaction:
    """
    Sends payment to the provider and records the transaction.
    Raises PaymentDeclinedException if the bank declines.

    items shape: [{ product_id, name, quantity, unit_price, unit_tax, subtotal }]
    billing_address shape: { street, apartment, city, state, postal_code, country }
    """

    provider = PaymentProvider.objects.filter(is_default=True).first()
    if not provider:
        raise ValueError("No payment provider configured")

    
    # TODO: replace with real gateway call (Stripe, Azul, etc.)
    # response = gateway.charge(
    #     card_number=card_number,
    #     expiry_month=expiry_month,
    #     expiry_year=expiry_year,
    #     cvv=cvv,
    #     cardholder_name=cardholder_name,
    #     billing_address=billing_address,
    #     currency="DOP",
    #     amount=amount,
    #     tax=tax_amount,
    #     line_items=items,
    # )
    # if not response.approved:
    #     raise PaymentDeclinedException(response.decline_reason)

    reference = str(uuid.uuid4())

    transaction = PaymentProviderTransaction.objects.create(
        payment_provider=provider,
        reference_document=reference,
        amount=amount,
        tax=tax_amount,
    )

    return transaction
