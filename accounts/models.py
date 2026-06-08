from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("status", "active")
        extra_fields.setdefault("role", "employee")

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("deactivated", "Deactivated"),
        ("deleted", "Deleted"),
    ]

    ROLE_CHOICES = [
        ("customer", "Customer"),
        ("employee", "Employee"),
    ]

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    # required by Django admin/auth
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    class Meta:
        db_table = "core_user"


    def __str__(self):
        return self.email



class Customer_model(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="customer_profile"
    )

    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "core_customer"

    def __str__(self):
        return f"Customer: {self.user.email}"

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
    class Meta:
        db_table = "core_employee"

    def __str__(self):
        return f"Employee: {self.user.email} ({self.position})"

