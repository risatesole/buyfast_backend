from ...inventory.services.stock_decrement import stock_decrement

def sell_product(product, user) -> None:
    """Processes a product sale by decrementing inventory."""
    stock_decrement(
        product=product,
        quantity=1,
        reference=f"BUY-{product.id}-{user.id}"  # type: ignore
    )
