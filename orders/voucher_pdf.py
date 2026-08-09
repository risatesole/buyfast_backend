from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

STATUS_LABELS_ES = {
    "awaiting_payment": "Esperando pago",
    "pending": "Pendiente",
    "fulfilled": "Entregado",
    "returned": "Devuelto",
    "cancelled": "Cancelada",
}


def build_order_voucher_pdf(order):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        title=f"Comprobante de pedido #{order.id}",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "VoucherTitle", parent=styles["Title"], fontSize=16, spaceAfter=2
    )
    subtitle_style = ParagraphStyle(
        "VoucherSubtitle", parent=styles["Normal"], alignment=1, fontSize=11
    )
    section_style = ParagraphStyle(
        "VoucherSection", parent=styles["Heading3"], fontSize=10, spaceAfter=4
    )
    body_style = styles["Normal"]
    footer_style = ParagraphStyle(
        "VoucherFooter", parent=styles["Normal"], alignment=1, fontSize=9, textColor=colors.grey
    )

    elements = [
        Paragraph("ECONOMATO UASD", title_style),
        Paragraph("Comprobante de Compra", subtitle_style),
        Spacer(1, 10 * mm),
    ]

    order_info = [
        [
            f"Número de pedido: {order.id}",
            f"Estado: {STATUS_LABELS_ES.get(order.status, order.get_status_display())}",
        ],
        [
            f"Fecha: {order.created_at.strftime('%d/%m/%Y %I:%M %p')}",
            f"Hora de recogida: {order.pickup_time.strftime('%d/%m/%Y %I:%M %p') if order.pickup_time else 'N/A'}",
        ],
    ]
    info_table = Table(order_info, colWidths=[85 * mm, 85 * mm])
    info_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 6 * mm))

    elements.append(Paragraph("Cliente", section_style))
    customer = order.customer
    customer_lines = [f"{customer.first_name} {customer.last_name}", customer.email]
    if customer.matricula:
        customer_lines.append(f"Matrícula: {customer.matricula}")
    for line in customer_lines:
        elements.append(Paragraph(line, body_style))
    elements.append(Spacer(1, 8 * mm))

    table_data = [["Producto", "Cant.", "Precio", "Impuesto", "Subtotal"]]
    total = 0
    for item in order.items.all():
        subtotal = item.subtotal
        total += subtotal
        table_data.append([
            f"{item.product.product.name} - {item.product.name}",
            str(item.quantity),
            f"RD$ {item.price_per_item:.2f}",
            f"RD$ {item.tax_amount:.2f}",
            f"RD$ {subtotal:.2f}",
        ])

    items_table = Table(table_data, colWidths=[70 * mm, 18 * mm, 27 * mm, 27 * mm, 28 * mm])
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#002d62")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 4 * mm))

    total_table = Table([["Total", f"RD$ {total:.2f}"]], colWidths=[142 * mm, 28 * mm])
    total_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LINEABOVE", (0, 0), (-1, 0), 1, colors.black),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(total_table)
    elements.append(Spacer(1, 14 * mm))

    elements.append(Paragraph("Gracias por su compra en el Economato UASD.", footer_style))

    doc.build(elements)
    return buffer.getvalue()
