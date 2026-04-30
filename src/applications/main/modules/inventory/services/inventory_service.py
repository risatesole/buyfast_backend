from django.utils import timezone
from django.db import transaction
from ..models.stock_entry_model import StockEntry
from ..models.stock_movement import StockMovement_model

class InventoryService:

    @staticmethod
    @transaction.atomic
    def add_inventory_entry(
        product,
        provider,
        metric_unit,
        quantity,
        cost_per_unit,
        added_by=None,
        note=None
    ):
        # 1. Create StockEntry
        entry = StockEntry.objects.create(
            product=product,
            provider=provider,
            metric_unit=metric_unit,
            quantity=quantity,
            cost_per_unit=cost_per_unit,
            added_by=added_by,
            note=note
        )

        # 2. Get last balance
        last_movement = (
            StockMovement_model.objects
            .filter(product=product)
            .order_by("-date_time")
            .first()
        )

        last_balance = last_movement.balance if last_movement else 0

        # 3. Calculate new balance
        new_balance = last_balance + quantity

        # 4. Create StockMovement
        StockMovement_model.objects.create(
            date_time=timezone.now(),
            product=product,
            movement_type="purchase_entry",
            document_reference=f"ENTRY-{entry.id}",
            quantity=quantity,
            balance=new_balance
        )

        return entry
