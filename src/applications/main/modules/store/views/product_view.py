from django.shortcuts import render, get_object_or_404
from ...product.models.model_product import Product

def storefront_product_page(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    return render(request, "store/product/product_page.html", {
        "product": product
    })



from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from ...inventory.models.stock_movement import StockMovement_model
from ...product.models.model_product import Product


@login_required
def store_front_buy_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":

        with transaction.atomic():

            # get current balance from last movement
            last_movement = (
                StockMovement_model.objects
                .filter(product=product)
                .order_by("-id")
                .first()
            )

            previous_balance = last_movement.balance if last_movement else 0

            # we sell 1 unit
            quantity_sold = 1
            new_balance = previous_balance - quantity_sold

            # register SALE movement
            StockMovement_model.objects.create(
                product=product,
                movement_type="customer_sell",
                quantity=quantity_sold,
                balance=new_balance,
                document_reference=f"BUY-{product.id}-{request.user.id}", # type: ignore
            )

            # deactivate product if no stock left
            if new_balance <= 0:
                product.status = "DEACTIVATED"
                product.save()

    return redirect("product_page", product_id=product.id) # type: ignore
