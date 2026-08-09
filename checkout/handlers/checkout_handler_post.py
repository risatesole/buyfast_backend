from .validators.validate_product_available import validation_product_avialability
from inventory.inventory import ProductUnavailableException, sell_products
from orders.orders import create_order
from django.db import transaction
from products.default.models import ProductVariant
from accounts.models import User
from rest_framework.response import Response
from rest_framework import status
from cart.models import CartItem
from django.core.mail import send_mail


def send_order_confirmation_email(order):
    print(f"Sending email:")
    lines = [
        f"Estimado(a) {order.customer.first_name} {order.customer.last_name},",
        "",
        "¡Gracias por su compra en el Economato UASD!",
        "",
        f"Su pedido #{order.id} ha sido recibido correctamente.",
        "",
        "Detalles del pedido:",
        "-" * 40,
    ]

    total = 0

    for item in order.items.all():
        subtotal = item.subtotal
        total += subtotal

        lines.extend([
            f"• {item.product.product.name} - {item.product.name}",
            f"  Cantidad: {item.quantity}",
            f"  Precio: RD$ {item.price_per_item:.2f}",
            f"  Impuestos: RD$ {item.tax_amount:.2f}",
            f"  Subtotal: RD$ {subtotal:.2f}",
            "",
        ])

    lines.extend([
        "-" * 40,
        f"Total: RD$ {total:.2f}",
        "",
        f"Hora de recogida: {order.pickup_time}",
        "",
        "Puede pasar a retirar su pedido en la fecha y hora seleccionadas.",
        "",
        "Atentamente,",
        "Equipo del Economato UASD",
    ])

    send_mail(
        subject=f"Confirmación de pedido #{order.id}",
        message="\n".join(lines),
        recipient_list=[order.customer.email],
        from_email=None,
        fail_silently=False,
    )

def remove_cart_item(items, user):
    from cart.models import Cart  # Import Cart model
    
    try:
        # Get the user's cart
        cart = Cart.objects.get(user=user)
        
        for item in items:
            product_variant_id = item.get("productvariantid")
            
            try:
                product_variant = ProductVariant.objects.get(id=product_variant_id)
                cart_item = CartItem.objects.get(
                    cart=cart,  # Use cart instead of user
                    variant=product_variant
                )
                cart_item.delete()
            except ProductVariant.DoesNotExist:
                print(f"Product variant {product_variant_id} not found")
            except CartItem.DoesNotExist:
                print(f"Cart item not found for cart {cart.id} and variant {product_variant_id}")
    except Cart.DoesNotExist:
        print(f"Cart not found for user {user}")


def create_order_checkout(
    user,
    billing_contact_firstname,
    billing_contact_lastname,
    billing_contact_email,
    billing_contact_phone_number,
    billing_address_street,
    billing_address_apartment,
    billing_address_city,
    billing_address_country,
    billing_address_postal_code,
    billing_address_state,
    pickuptime,
    items
):
    """
    Creates the order and reserves stock for it, leaving it in
    AWAITING_PAYMENT. The cart is only cleared and the confirmation email
    only sent once PayPal capture succeeds (see payment/views/paypal_api_view.py).
    """

    is_product_avialable = validation_product_avialability(items)
    order = create_order(user, items, pickuptime)
    sell_products(items, f"Order #{order.id} reserved")
    return order


def checkout_handler_post(request):
    # billing contact
    user = request.user
    billing_contact_firstname = request.data["billing_contact"]["firstname"]
    billing_contact_lastname =  request.data["billing_contact"]["lastname"]
    billing_contact_email=  request.data["billing_contact"]["email"]
    billing_contact_phone_number=  request.data["billing_contact"]["phone_number"]

    billing_address_street = request.data["billing_address"]["street"]
    billing_address_apartment =request.data["billing_address"]["apartment"] 
    billing_address_city = request.data["billing_address"]["city"] 
    billing_address_country = request.data["billing_address"]["country"]
    billing_address_postal_code = request.data["billing_address"]["postal_code"]
    billing_address_state = request.data["billing_address"]["state"]

    pickuptime = request.data["pickuptime"]

    items = request.data.get("items", [])
    try:
        order = create_order_checkout(
                user,
                billing_contact_firstname,
                billing_contact_lastname,
                billing_contact_email,
                billing_contact_phone_number,
                billing_address_street,
                billing_address_apartment,
                billing_address_city,
                billing_address_country,
                billing_address_postal_code,
                billing_address_state,
                pickuptime,
                items
            )

        amount = sum(item.subtotal for item in order.items.all())

        return Response(
                    {
                        "success": True,
                        "status": "ok",
                        "message": "Checkout successful",
                        "order_id": order.id,
                        "amount": amount,
                    }
                )

    except ProductUnavailableException as e:
        return Response(
            {
                "success": False,
                "status": "error",
                "error": {
                    "message": "some products are unavialable",
                    "products": f"{e}"
                }
            },
            status=400
        ) 