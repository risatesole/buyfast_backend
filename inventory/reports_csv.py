# inventory/reports_csv.py
import csv
from io import StringIO

from .reports_pdf import MOVEMENT_TYPE_LABELS_ES, inventory_status_label


def build_inventory_stock_report_csv(variants):
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Producto", "SKU", "Categoría", "Cantidad", "Estado", "Precio"])

    for variant in variants:
        quantity = getattr(variant, "total_quantity", 0)
        writer.writerow([
            f"{variant.product.name} - {variant.name}",
            variant.sku,
            variant.product.category.name,
            quantity,
            inventory_status_label(quantity),
            f"{variant.selling_price:.2f}",
        ])

    return buffer.getvalue().encode("utf-8-sig")


def build_inventory_movements_report_csv(movements):
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Fecha", "Producto", "SKU", "Tipo", "Cantidad", "Balance"])

    for movement in movements:
        variant = movement.product_variant
        writer.writerow([
            movement.date_time.strftime("%d/%m/%Y %I:%M %p"),
            f"{variant.product.name} - {variant.name}",
            variant.sku,
            MOVEMENT_TYPE_LABELS_ES.get(movement.movement_type, movement.movement_type),
            movement.quantity,
            movement.balance,
        ])

    return buffer.getvalue().encode("utf-8-sig")
