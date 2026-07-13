from .validators.validate_product_available import validation_product_avialability
from payment.payment import validate_credit_card, InvalidCreditCardError
from payment.payment import validate_credit_card, InvalidCreditCardError, process_payment, PaymentDeclinedException
from inventory.inventory import ProductUnavailableException, sell_products
from orders.orders import create_order
from django.db import transaction
from products.default.models import ProductVariant
from accounts.models import User
from rest_framework.response import Response
from rest_framework import status
from cart.cart import clear_cart

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
    create_order(user,items,pickuptime)

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

        

        return Response(
                    {
                        "success": True,
                        "status": "ok",
                        "message": "Checkout successful",
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
                    "message": "some products are unavialable",
                    "products": f"{e}"
                }
            },
            status=400
        ) 