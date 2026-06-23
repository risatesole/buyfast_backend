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
    tax: float = 0,
    items: list = [],
) -> PaymentProviderTransaction:
    """
    Sends payment to the provider and records the transaction.
    Raises PaymentDeclinedException if the bank declines.
    """

    provider = PaymentProvider.objects.filter(name="default").first()
    if not provider:
        raise ValueError("No payment provider configured")

    # TODO: replace with real gateway call (Stripe, Azul, etc.)
    # response = gateway.charge(
    #     card_number=card_number,
    #     expiry_month=expiry_month,
    #     expiry_year=expiry_year,
    #     cvv=cvv,
    #     currency="DOP",
    #     amount=amount,
    #     tax=tax,
    #     line_items=items,  # [{ product_id, name, quantity, unit_price, unit_tax, subtotal }]
    # )
    # if not response.approved:
    #     raise PaymentDeclinedException(response.decline_reason)

    reference = str(uuid.uuid4())

    transaction = PaymentProviderTransaction.objects.create(
        payment_provider=provider,
        reference_document=reference,
        amount=amount,
        tax=tax,
    )

    return transaction