from django.db import transaction
from ..models import Order, OrderItem, OrderPayment
from products.default.models import ProductVariant

# def create_order(customer, items, payment_transaction,pickuptime):
def create_order(customer, items,pickuptime):
    print(f"executing create order")
    print(f"customer credentials:")
    print(f"id: {customer.id}")
    print(f"first name{customer.first_name}")


    print(f"creating the order:")
    order = Order.objects.create(
        customer = customer,
        pickup_time=pickuptime,
    )

    for item in items:
        quantity = item["quantity"]
        product_variant_id = int(item["productvariantid"])
        productvariant = ProductVariant.objects.get(id=product_variant_id)
        
        print(f"product name: {productvariant.name}")
        print(f"Quantity: {quantity}")

        price = productvariant.selling_price
        taxrate = productvariant.tax_rate
        tax_amount =price * taxrate

        order_item = OrderItem.objects.create(
            order=order,
            product = productvariant,
            quantity=quantity,
            price_per_item= productvariant.selling_price,
            tax_amount=tax_amount
        )

    return order
