import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from notifications.formatting import format_currency_dop, format_pickup_time

logger = logging.getLogger(__name__)


def _send_email(subject, template_name, context, to_email, text_body=None):
    html_body = render_to_string(f"notifications/emails/{template_name}", context)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body or strip_tags(html_body),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    email.attach_alternative(html_body, "text/html")

    try:
        email.send(fail_silently=False)
        return True
    except Exception:
        logger.exception("Failed to send email %r to %s", subject, to_email)
        return False


def send_welcome_email(*, to_email, first_name, last_name, matricula, verify_link):
    return _send_email(
        subject="¡Bienvenido al Económato UASD!",
        template_name="verify_email.html",
        context={
            "is_welcome": True,
            "to_email": to_email,
            "first_name": first_name,
            "last_name": last_name,
            "matricula": matricula,
            "verify_link": verify_link,
        },
        to_email=to_email,
    )


def send_verification_email(*, to_email, first_name, last_name, verify_link):
    return _send_email(
        subject="Verifica tu correo - Económato UASD",
        template_name="verify_email.html",
        context={
            "is_welcome": False,
            "to_email": to_email,
            "first_name": first_name,
            "last_name": last_name,
            "verify_link": verify_link,
        },
        to_email=to_email,
    )


def send_password_reset_email(*, to_email, first_name, last_name, reset_link):
    return _send_email(
        subject="Recupera tu contraseña - Económato UASD",
        template_name="password_reset.html",
        context={
            "first_name": first_name,
            "last_name": last_name,
            "reset_link": reset_link,
        },
        to_email=to_email,
    )


def send_order_confirmation_email(*, to_email, first_name, last_name, order_id, pickup_time, items, total):
    items_display = [
        {
            "product_name": item["product_name"],
            "variant_name": item.get("variant_name"),
            "quantity": item["quantity"],
            "price_per_item_display": format_currency_dop(item["price_per_item"]),
            "tax_amount_display": format_currency_dop(item["tax_amount"]),
            "subtotal_display": format_currency_dop(item["subtotal"]),
        }
        for item in items
    ]
    pickup_time_display = format_pickup_time(pickup_time)
    total_display = format_currency_dop(total)

    text_lines = [
        f"Estimado(a) {first_name} {last_name},",
        "",
        "¡Gracias por su compra en el Económato UASD!",
        "",
        f"Su pedido #{order_id} ha sido recibido correctamente.",
        "",
        "Detalles del pedido:",
        "-" * 40,
    ]
    for item, display in zip(items, items_display):
        name = item["product_name"]
        if item.get("variant_name"):
            name += f" - {item['variant_name']}"
        text_lines.extend([
            f"• {name}",
            f"  Cantidad: {item['quantity']}",
            f"  Precio: {display['price_per_item_display']}",
            f"  Impuestos: {display['tax_amount_display']}",
            f"  Subtotal: {display['subtotal_display']}",
            "",
        ])
    text_lines.extend([
        "-" * 40,
        f"Total: {total_display}",
        "",
        f"Hora de recogida: {pickup_time_display}",
        "",
        "Puede pasar a retirar su pedido en la fecha y hora seleccionadas.",
        "",
        "Atentamente,",
        "Equipo del Económato UASD",
    ])

    return _send_email(
        subject=f"Confirmación de pedido #{order_id}",
        template_name="order_confirmation.html",
        context={
            "first_name": first_name,
            "last_name": last_name,
            "order_id": order_id,
            "pickup_time_display": pickup_time_display,
            "items": items_display,
            "total_display": total_display,
        },
        to_email=to_email,
        text_body="\n".join(text_lines),
    )


def send_order_fulfilled_email(*, to_email, first_name, last_name, order_id, pickup_time):
    return _send_email(
        subject=f"Confirmación de entrega del pedido #{order_id}",
        template_name="order_fulfilled.html",
        context={
            "first_name": first_name,
            "last_name": last_name,
            "order_id": order_id,
            "pickup_time_display": format_pickup_time(pickup_time),
        },
        to_email=to_email,
    )
