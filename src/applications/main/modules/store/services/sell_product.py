from .create_order import create_order_from_product
from ...inventory.services.stock_decrement import stock_decrement


def sell_product(product, user) -> None:
    """Processes a product sale by creating an order and updating inventory."""

    # 1. Create order
    order = create_order_from_product(product, user)

    # 2. Decrement stock
    stock_decrement(
        product=product,
        quantity=1,
        reference=f"BUY-{product.id}-{user.id}"  # type: ignore
    )
