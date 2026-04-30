from .modules.account.user.models.model_user import User  as User
from .modules.account.user.models.model_user import UserRoles as UserRoles
from .modules.product.models.model_product import Product as Product 
from .modules.account.user.models.customer_profile import Customer_model as Customer_model
from .modules.account.user.models.employee_profile import Employee as Employee
from .modules.inventory.models.provider_model import Provider as Provider
from .modules.inventory.models.inventory_recipt_model import StockEntry as StockEntry

from django.db import models
from django.utils import timezone

class Batch(models.Model):
    class Meta:
        db_table = "batch"
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    provider = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="provided_batches",
        limit_choices_to={"role": UserRoles.CUSTOMER} # TODO: make this provider
    )

    accepted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accepted_batches",
        limit_choices_to={"role": UserRoles.CUSTOMER} # TODO: make this employee
    )
    unitperbatch = models.IntegerField()
    acquisition_price = models.FloatField()
    datetime = models.DateTimeField(null=True, blank=True)
