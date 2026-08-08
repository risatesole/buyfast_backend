# inventory/reports_pdf.py
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

INVENTORY_STATUS_LABELS_ES = {
    "in_stock": "En Stock",
    "medium_stock": "Stock Medio",
    "low_stock": "Stock Bajo",
    "out_of_stock": "Sin Stock",
}

MOVEMENT_TYPE_LABELS_ES = {
    "purchase_entry": "Entrada por Compra",
    "customer_sell": "Salida por Venta",
    "initial_inventory": "Inventario Inicial",
    "manual_decrease": "Salida Manual",
}


def inventory_status_label(quantity):
    if quantity <= 0:
        return INVENTORY_STATUS_LABELS_ES["out_of_stock"]
    if quantity <= 10:
        return INVENTORY_STATUS_LABELS_ES["low_stock"]
    if quantity <= 50:
        return INVENTORY_STATUS_LABELS_ES["medium_stock"]
    return INVENTORY_STATUS_LABELS_ES["in_stock"]


def _build_report_doc(title, filters_summary):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        title=title,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("ReportTitle", parent=styles["Title"], fontSize=16, spaceAfter=2)
    subtitle_style = ParagraphStyle(
        "ReportSubtitle", parent=styles["Normal"], alignment=1, fontSize=11
    )
    filters_style = ParagraphStyle(
        "ReportFilters", parent=styles["Normal"], alignment=1, fontSize=9, textColor=colors.grey
    )

    elements = [
        Paragraph("ECONOMATO UASD", title_style),
        Paragraph(title, subtitle_style),
        Spacer(1, 4 * mm),
        Paragraph(filters_summary, filters_style),
        Spacer(1, 8 * mm),
    ]
    return buffer, doc, elements


def _styled_table(table_data, col_widths):
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#002d62")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def build_inventory_stock_report_pdf(variants, filters_summary):
    buffer, doc, elements = _build_report_doc("Reporte de Inventario — Estado Actual", filters_summary)

    table_data = [["Producto", "SKU", "Categoría", "Cantidad", "Estado", "Precio"]]
    for variant in variants:
        quantity = getattr(variant, "total_quantity", 0)
        table_data.append([
            f"{variant.product.name} - {variant.name}",
            variant.sku,
            variant.product.category.name,
            str(quantity),
            inventory_status_label(quantity),
            f"RD$ {variant.selling_price:.2f}",
        ])

    elements.append(_styled_table(
        table_data, col_widths=[55 * mm, 30 * mm, 30 * mm, 20 * mm, 25 * mm, 25 * mm]
    ))
    doc.build(elements)
    return buffer.getvalue()


def build_inventory_movements_report_pdf(movements, filters_summary):
    buffer, doc, elements = _build_report_doc("Reporte de Inventario — Movimientos", filters_summary)

    table_data = [["Fecha", "Producto", "SKU", "Tipo", "Cantidad", "Balance"]]
    for movement in movements:
        variant = movement.product_variant
        table_data.append([
            movement.date_time.strftime("%d/%m/%Y %I:%M %p"),
            f"{variant.product.name} - {variant.name}",
            variant.sku,
            MOVEMENT_TYPE_LABELS_ES.get(movement.movement_type, movement.movement_type),
            str(movement.quantity),
            str(movement.balance),
        ])

    elements.append(_styled_table(
        table_data, col_widths=[28 * mm, 55 * mm, 28 * mm, 32 * mm, 20 * mm, 22 * mm]
    ))
    doc.build(elements)
    return buffer.getvalue()
