from django.db import transaction
from inventory.models import StockMovement_model
from inventory.inventory import ProductUnavailableException

def sell_products(items, order_reference: str):
    """
    Decreases inventory for each item in the order.
    Raises ProductUnavailableException if any product has insufficient stock.
    All movements are created atomically — if one fails, none are recorded.

    items         — [{ productvariantid, quantity }]
    order_reference — order id or reference string for document_reference
    """

    print(f"####################### executing sell_product()")

    with transaction.atomic():
        for item in items:
            # Get the product variant ID from the item
            product_variant_id = item["productvariantid"]
            qty = item["quantity"]

            # Get the latest stock movement for this product variant
            latest_movement = (
                StockMovement_model.objects
                .filter(product_variant_id=product_variant_id)  # ✅ Fixed: use product_variant_id
                .order_by("-date_time")
                .select_for_update()  # ← locks the row to prevent race conditions
                .first()
            )
            
            # Check if product exists in inventory
            if not latest_movement:
                raise ProductUnavailableException([{
                    'product_variant_id': product_variant_id,
                    'message': 'Product not found in inventory'
                }])
            
            # Check if enough stock is available
            if latest_movement.balance < qty:
                raise ProductUnavailableException([{
                    'product_variant_id': product_variant_id,
                    'available': latest_movement.balance,
                    'requested': qty,
                    'message': f'Insufficient stock. Available: {latest_movement.balance}, Requested: {qty}'
                }])

            # Calculate new balance
            new_balance = latest_movement.balance - qty

            # ✅ Create the stock movement record
            StockMovement_model.objects.create(
                product_variant_id=product_variant_id,  # ✅ Fixed: use product_variant_id
                movement_type="customer_sell",
                document_reference=str(order_reference),
                quantity=qty,  # This is the quantity sold (positive number)
                balance=new_balance,  # The new balance after sale
            )
            
