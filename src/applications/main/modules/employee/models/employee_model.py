from django.db import models
from ...account.user.models.model_user import User


class EmployeePosition(models.TextChoices):
    ADMIN = "admin", "System Administrator"
    STORE_MANAGER = "store_manager", "Store Manager"
    ORDER_MANAGER = "order_manager", "Order Manager"
    INVENTORY_MANAGER = "inventory_manager", "Inventory Manager"
    CUSTOMER_SUPPORT = "customer_support", "Customer Support"
    LOGISTICS = "logistics", "Logistics / Shipping"
    CONTENT_MANAGER = "content_manager", "Content Manager"
    FINANCE = "finance", "Finance / Accounting"

class employee_model(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="employee_profile"
    )

    position = models.CharField(
        max_length=20,
        choices=EmployeePosition.choices,
        default=EmployeePosition.STORE_MANAGER
    )

    hired_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Employee: {self.user.email} ({self.position})"
