
from .validators.validate_product_available import validation_product_avialability
from payment.payment import validate_credit_card, InvalidCreditCardError
from payment.payment import validate_credit_card, InvalidCreditCardError, process_payment, PaymentDeclinedException
from inventory.inventory import ProductUnavailableException, sell_products
from orders.orders import create_order
from django.db import transaction
from products.models import Product
from accounts.models import User
from rest_framework.response import Response
from rest_framework import status
from cart.cart import clear_cart

def build_line_items(items) -> tuple[list, float, float]:
    product_ids = [item["productid"] for item in items]
    products = Product.objects.filter(id__in=product_ids)
    price_map    = {p.id: p.selling_price for p in products}
    name_map     = {p.id: p.name          for p in products}
    tax_rate_map = {p.id: p.tax_rate      for p in products}  # ← from Product model

    line_items = []
    total_amount = 0.0
    total_tax = 0.0

    for item in items:
        pid        = item["productid"]
        qty        = item["quantity"]
        unit_price = float(price_map.get(pid, 0))
        tax_rate   = float(tax_rate_map.get(pid, 0))  # ← no more hardcoded 0.18

        unit_tax = round(unit_price * tax_rate, 2)
        subtotal = round((unit_price + unit_tax) * qty, 2)

        line_items.append({
            "product_id": pid,
            "name":       name_map.get(pid, "Unknown product"),
            "quantity":   qty,
            "unit_price": unit_price,
            "unit_tax":   unit_tax,
            "subtotal":   subtotal,
        })

        total_amount += unit_price * qty
        total_tax    += unit_tax   * qty

    return line_items, round(total_amount, 2), round(total_tax, 2)



def calculate_total(items) -> float:
    product_ids = [item["productid"] for item in items]
    products = Product.objects.filter(id__in=product_ids)
    price_map = {p.id: p.selling_price for p in products}

    total = sum(
        price_map[item["productid"]] * item["quantity"]
        for item in items
        if item["productid"] in price_map
    )
    return float(total)

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
    card_information_card_number,
    card_information_expiry_month,
    card_information_expiry_year,
    card_information_cvv,
    pickuptime,
    items
):
    is_card_valid = validate_credit_card(
        card_information_card_number,
        card_information_expiry_month,
        card_information_expiry_year,
        card_information_cvv
    )
    is_product_avialable = validation_product_avialability(items)

    line_items, total_amount, total_tax = build_line_items(items)
    payment_transaction = process_payment(
        card_number=card_information_card_number,
        expiry_month=card_information_expiry_month,
        expiry_year=card_information_expiry_year,
        cvv=card_information_cvv,
        amount=total_amount,
        tax_amount=total_tax,
        items=line_items,
        cardholder_name=f"{billing_contact_firstname} {billing_contact_lastname}",
        billing_address={
            "street":      billing_address_street,
            "apartment":   billing_address_apartment,
            "city":        billing_address_city,
            "state":       billing_address_state,
            "postal_code": billing_address_postal_code,
            "country":     billing_address_country,
        }
    )

    with transaction.atomic():
        order = create_order(
            customer=user,
            line_items=line_items,
            payment_transaction=payment_transaction,
            pickuptime = pickuptime,
        )

        sell_products(
            items=[{"product_id": item["product_id"], "quantity": item["quantity"]} for item in line_items],
            order_reference=order.id,
        )

        clear_cart(user)
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

    card_information_card_number = request.data["card_information"]["card_number"]
    card_information_expiry_month = request.data["card_information"]["expiry_month"]
    card_information_expiry_year = request.data["card_information"]["expiry_year"]
    card_information_cvv = request.data["card_information"]["cvv"]

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
                card_information_card_number,
                card_information_expiry_month,
                card_information_expiry_year,
                card_information_cvv,
                pickuptime,
                items
            )

        order_items = [
            {
                "id": item.id,
                "product": {
                    "id": item.product.id,
                    "name": item.product.name,
                },
                "quantity": item.quantity,
                "price_per_item": item.price_per_item,
                "tax_amount": item.tax_amount,
                "subtotal": item.subtotal,
            }
            for item in order.items.select_related("product").all()
        ]

        return Response(
                    {
                        "success": True,
                        "status": "ok",
                        "message": "Checkout successful",
                        "data": {
                            "order": {
                                "id": order.id,
                                "pickuptime": pickuptime,
                                "items": order_items,
                            }
                        }
                    }
                )

    except InvalidCreditCardError as e:
        return Response({"success": False, "message": "Invalid credit card","error":{"message":"invalid credit card"}},status=status.HTTP_400_BAD_REQUEST)

    except ProductUnavailableException as e:
        return Response(
            {
                "success": False,
                "status": "error",
                "error": {
                    "message": "some products are unavialable"
                }
            },
            status=400
        )

