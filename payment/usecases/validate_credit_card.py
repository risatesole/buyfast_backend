from datetime import datetime

class InvalidCreditCardError(Exception):
    def __init__(self, message="No pudimos procesar la tarjeta. Verifica los datos e intenta nuevamente."):
        self.message = message
        super().__init__(self.message)


def validate_credit_card(card_number: str, expiry_month: int, expiry_year: int, cvv: int) -> None:

    now = datetime.now()
    if not (1 <= expiry_month <= 12):
        raise InvalidCreditCardError("Invalid expiry month")

    if expiry_year < 100:
        expiry_year += 2000

    if expiry_year < now.year:
        raise InvalidCreditCardError("Card has expired")

    if expiry_year == now.year and expiry_month < now.month:
        raise InvalidCreditCardError("Card has expired")

    card_number = card_number.replace(" ", "").replace("-", "")

    if not card_number.isdigit():
        raise InvalidCreditCardError("Card number must contain only digits")

    total = 0
    reverse_digits = card_number[::-1]

    for i, digit in enumerate(reverse_digits):
        n = int(digit)

        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9

        total += n

    if total % 10 != 0:
        raise InvalidCreditCardError("Invalid card number")
