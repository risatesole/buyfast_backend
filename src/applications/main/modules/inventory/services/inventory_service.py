from django.utils import timezone
from django.db import transaction
from ..models.stock_entry_model import StockEntry
from ..models.stock_movement import StockMovement_model
from ..models.provider_model import Provider
class InventoryService:

    @staticmethod
    def list_providers():
        return Provider.objects.all()

    @staticmethod
    @transaction.atomic
    def add_inventory_entry(
        product,
        provider,
        quantity,
        cost_per_unit,
        added_by=None,
        note=None
    ):
        # Optional: remove debug prints in production
        # print(type(quantity))

        entry = StockEntry.objects.create(
            product=product,
            provider=provider,
            quantity=quantity,
            cost_per_unit=cost_per_unit,
            added_by=added_by,
            note=note
        )

        last_movement = (
            StockMovement_model.objects
            .filter(product=product)
            .order_by("-date_time")
            .first()
        )

        last_balance = last_movement.balance if last_movement else 0
        new_balance = last_balance + quantity

        StockMovement_model.objects.create(
            date_time=timezone.now(),
            product=product,
            movement_type="purchase_entry",
            document_reference=f"ENTRY-{entry.id}", # type: ignore
            quantity=quantity,
            balance=new_balance
        )

        return entry

    @staticmethod
    def list_stock_movements():
        return (
            StockMovement_model.objects
            .select_related("product")
            .order_by("-date_time")
        )

    @staticmethod
    def list_stock_entries():
        return (
            StockEntry.objects
            .select_related("product", "provider", "added_by")
            .order_by("-received_at")
        )


    @staticmethod
    def get_stock():
        movements = StockMovement_model.objects.select_related("product").order_by("-date_time")

        seen_products = set()
        inventory = []

        for movement in movements:
            product_id = movement.product.id

            if product_id in seen_products:
                continue

            seen_products.add(product_id)

            inventory.append({
                "id": product_id,
                "product_name": movement.product.name,
                "stock_quantity": movement.balance,
                "metric_unit": movement.product.metric_unit,
                "status": "In Stock"
            })

        return {"inventory": inventory}