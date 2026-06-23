from ..models import CartItem

def clear_cart(user) -> None:
    CartItem.objects.filter(user=user).delete()
