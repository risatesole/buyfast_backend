# accounts/reports_csv.py
import csv
from io import StringIO

from .reports_pdf import POSITION_LABELS_ES


def build_employees_report_csv(employees):
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Nombre", "Email", "Posición", "Perfil", "Fecha de Contratación", "Estado"])

    for user in employees:
        employee = getattr(user, "employee_profile", None)
        position = getattr(employee, "position", None)
        profile = getattr(employee, "profile", None)
        hired_at = getattr(employee, "hired_at", None)
        writer.writerow([
            f"{user.first_name} {user.last_name}",
            user.email,
            POSITION_LABELS_ES.get(position, position or "N/A"),
            profile.name if profile else "Sin perfil",
            hired_at.strftime("%d/%m/%Y") if hired_at else "N/A",
            "Activo" if user.is_active else "Inactivo",
        ])

    return buffer.getvalue().encode("utf-8-sig")


def build_customers_report_csv(customers):
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Nombre", "Email", "Matrícula", "Miembro UASD", "Fecha de Registro", "Compras"])

    for user in customers:
        writer.writerow([
            f"{user.first_name} {user.last_name}",
            user.email,
            user.matricula or "N/A",
            "Sí" if user.institution_member else "No",
            user.created_at.strftime("%d/%m/%Y"),
            getattr(user, "purchase_count", 0),
        ])

    return buffer.getvalue().encode("utf-8-sig")
