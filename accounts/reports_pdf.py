# accounts/reports_pdf.py
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

POSITION_LABELS_ES = {
    "admin": "Administrador",
    "store_manager": "Gerente de tienda",
    "order_manager": "Gerente de pedidos",
    "inventory_manager": "Gerente de inventario",
    "customer_support": "Atención al cliente",
    "logistics": "Logística",
    "content_manager": "Gerente de contenido",
    "finance": "Finanzas",
}

PAGE_WIDTH, _PAGE_HEIGHT = landscape(letter)
MARGIN = 16 * mm
USABLE_WIDTH = PAGE_WIDTH - 2 * MARGIN


def _scaled_col_widths(weights):
    """Rescales relative column-width weights so they always sum to exactly
    the page's usable width, regardless of page size/margins."""
    total_weight = sum(weights)
    return [USABLE_WIDTH * (weight / total_weight) for weight in weights]


def _build_report_doc(title, filters_summary):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
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


def build_employees_report_pdf(employees, filters_summary):
    buffer, doc, elements = _build_report_doc("Reporte de Empleados", filters_summary)

    table_data = [["Nombre", "Email", "Posición", "Perfil", "Fecha de Contratación", "Estado"]]
    for user in employees:
        employee = getattr(user, "employee_profile", None)
        position = getattr(employee, "position", None)
        profile = getattr(employee, "profile", None)
        hired_at = getattr(employee, "hired_at", None)
        table_data.append([
            f"{user.first_name} {user.last_name}",
            user.email,
            POSITION_LABELS_ES.get(position, position or "N/A"),
            profile.name if profile else "Sin perfil",
            hired_at.strftime("%d/%m/%Y") if hired_at else "N/A",
            "Activo" if user.is_active else "Inactivo",
        ])

    elements.append(_styled_table(
        table_data, col_widths=_scaled_col_widths([45, 55, 35, 35, 30, 20])
    ))
    doc.build(elements)
    return buffer.getvalue()


def build_customers_report_pdf(customers, filters_summary):
    buffer, doc, elements = _build_report_doc("Reporte de Clientes", filters_summary)

    table_data = [["Nombre", "Email", "Matrícula", "Miembro UASD", "Fecha de Registro", "Compras"]]
    for user in customers:
        table_data.append([
            f"{user.first_name} {user.last_name}",
            user.email,
            user.matricula or "N/A",
            "Sí" if user.institution_member else "No",
            user.created_at.strftime("%d/%m/%Y"),
            str(getattr(user, "purchase_count", 0)),
        ])

    elements.append(_styled_table(
        table_data, col_widths=_scaled_col_widths([45, 55, 25, 25, 30, 20])
    ))
    doc.build(elements)
    return buffer.getvalue()
