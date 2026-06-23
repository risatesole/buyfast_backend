from django.db import ProgrammingError
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status

from api.utils import CsrfExemptSessionAuthentication
from cart.models import CartItem
from products.models import Product
from accounts.models import User
from .validators.validate_product_available import validation_product_avialability
from payment.payment import validate_credit_card, InvalidCreditCardError
from inventory.inventory import ProductUnavailableException

from payment.payment import validate_credit_card, InvalidCreditCardError, process_payment, PaymentDeclinedException


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

def create_order(
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
    transaction = process_payment(
        card_number=card_information_card_number,
        expiry_month=card_information_expiry_month,
        expiry_year=card_information_expiry_year,
        cvv=card_information_cvv,
        amount=total_amount,
        tax=total_tax,
        items=line_items,
    )

    return {   
        "success": True,
        "message": "Order can be created",
        "items": items
    }



def checkout_handler_post(request):
    # billing contact
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
        order = create_order(
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

        return order
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
            status=200
        )



@api_view(["GET", "POST", "DELETE"])
@authentication_classes([CsrfExemptSessionAuthentication])
def checkout_api_view(request):
    try:
        user = request.user

        if not user.is_authenticated:
            return Response({
                "status": "error",
                "message": "Authentication required",
                "data": None
            }, status=401)

        if request.method == "GET":
            items = CartItem.objects.filter(user=user).select_related(
                "product", "product__category"
            ).prefetch_related("product__images", "product__tags")

            return Response({
                "status": "ok",
                "data": {
                    "cart": {
                        "items": [
                            {
                                "id": item.id,
                                "product": {
                                    "id": item.product.id,
                                    "name": item.product.name,
                                    "description": item.product.description,
                                    "brand": item.product.brand,
                                    "selling_price": item.product.selling_price,
                                    "status": item.product.status,
                                    "category": {
                                        "id": item.product.category.id,
                                        "name": item.product.category.name,
                                        "slug": item.product.category.slug,
                                        "image": item.product.category.image,
                                        "status": item.product.category.status,
                                    },
                                    "images": [
                                        {
                                            "url": image.image,
                                            "type": image.image_type,
                                        }
                                        for image in item.product.images.all()
                                    ],
                                    "tags": [
                                        tag.name
                                        for tag in item.product.tags.all()
                                    ],
                                },
                                "quantity": item.quantity,
                            }
                            for item in items
                        ]
                    },
                    "user": {
                        "id": user.id,
                        "firstname": user.first_name,   
                        "lastname": user.last_name,
                        "email": user.email,
                        "matricula": user.matricula,
                        "phone_number": user.phone_number,
                        "permissions": [],
                        "profilepicture": ""

                    }
                }
            })

        if request.method == "POST":
            return checkout_handler_post(request)
            













        if request.method == "DELETE":
            product_id = request.data.get("product_id")
            quantity = int(request.data.get("quantity", 1))

            if not product_id:
                return Response({
                    "status": "error",
                    "message": "product_id is required"
                }, status=400)

            if quantity < 1:
                return Response({
                    "status": "error",
                    "message": "quantity must be greater than 0"
                }, status=400)

            try:
                cart_item = CartItem.objects.get(
                    user=user,
                    product_id=product_id
                )
            except CartItem.DoesNotExist:
                return Response({
                    "status": "error",
                    "message": "Item not found in cart"
                }, status=404)

            cart_item.quantity -= quantity

            if cart_item.quantity <= 0:
                cart_item.delete()

                return Response({
                    "status": "ok",
                    "message": "Item removed from cart",
                    "data": {
                        "product_id": int(product_id),
                        "quantity": 0
                    }
                })

            cart_item.save()

            return Response({
                "status": "ok",
                "message": "Item quantity updated",
                "data": {
                    "product_id": int(product_id),
                    "quantity": cart_item.quantity
                }
            })

    except Product.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Product not found"
        }, status=404)

    except ProgrammingError:
        return Response({
            "status": "error",
            "message": (
                "Cart table does not exist. "
                "Run: python manage.py makemigrations cart && python manage.py migrate"
            )
        }, status=500)

    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),
            "data": None
        }, status=400)
