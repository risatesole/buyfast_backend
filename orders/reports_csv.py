# orders/reports_csv.py
import csv
from io import StringIO

from .voucher_pdf import STATUS_LABELS_ES


def build_orders_report_csv(orders):
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["ID", "Cliente", "Email", "Fecha", "Total", "Estado", "Recogida"])

    for order in orders:
        customer = order.customer
        total = getattr(order, "total_amount", 0) + getattr(order, "total_tax", 0)
        writer.writerow([
            order.pk,
            f"{customer.first_name} {customer.last_name}" if customer else "N/A",
            customer.email if customer else "N/A",
            order.created_at.strftime("%d/%m/%Y %I:%M %p"),
            f"{total:.2f}",
            STATUS_LABELS_ES.get(order.status, order.get_status_display()),
            order.pickup_time.strftime("%d/%m/%Y %I:%M %p") if order.pickup_time else "N/A",
        ])

    return buffer.getvalue().encode("utf-8-sig")
