from django.db import models
from django.core.exceptions import ValidationError
from ...account.user.models.model_user import User


class Order_model(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        limit_choices_to={"role": "customer"}  # filters in admin/forms
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """Ensures only users with role 'customer' can have orders."""
        if self.user.role != "customer":
            raise ValidationError("Order user must have role 'customer'")

    def save(self, *args, **kwargs):
        self.clean()  # enforce validation on save
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} - {self.user.email}" # type: ignore