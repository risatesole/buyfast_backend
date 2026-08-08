# orders/reports_pdf.py
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .voucher_pdf import STATUS_LABELS_ES


def build_orders_report_pdf(orders, filters_summary):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        title="Reporte de Pedidos",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Title"], fontSize=16, spaceAfter=2
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle", parent=styles["Normal"], alignment=1, fontSize=11
    )
    filters_style = ParagraphStyle(
        "ReportFilters", parent=styles["Normal"], alignment=1, fontSize=9, textColor=colors.grey
    )

    elements = [
        Paragraph("ECONOMATO UASD", title_style),
        Paragraph("Reporte de Pedidos", subtitle_style),
        Spacer(1, 4 * mm),
        Paragraph(filters_summary, filters_style),
        Spacer(1, 8 * mm),
    ]

    table_data = [["ID", "Cliente", "Email", "Fecha", "Total", "Estado", "Recogida"]]
    for order in orders:
        customer = order.customer
        total = getattr(order, "total_amount", 0) + getattr(order, "total_tax", 0)
        table_data.append([
            str(order.pk),
            f"{customer.first_name} {customer.last_name}" if customer else "N/A",
            customer.email if customer else "N/A",
            order.created_at.strftime("%d/%m/%Y %I:%M %p"),
            f"RD$ {total:.2f}",
            STATUS_LABELS_ES.get(order.status, order.get_status_display()),
            order.pickup_time.strftime("%d/%m/%Y %I:%M %p") if order.pickup_time else "N/A",
        ])

    table = Table(
        table_data,
        colWidths=[12 * mm, 40 * mm, 55 * mm, 30 * mm, 25 * mm, 22 * mm, 30 * mm],
        repeatRows=1,
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#002d62")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (4, 0), (4, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(table)

    doc.build(elements)
    return buffer.getvalue()
