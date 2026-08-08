# inventory/tests/test_stockmovement_decrease_api.py

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Profile, employee_model
from inventory.models import StockMovement_model, StockDecrease_model
from products.default.models import Category, Product, ProductVariant

User = get_user_model()


class StockMovementDecreaseAPITests(APITestCase):
    def setUp(self):
        self.employee = User.objects.create_user(
            email="stockclerk@example.com",
            password="Password123!",
            first_name="Stock",
            last_name="Clerk",
            role="employee",
        )
        profile = Profile.objects.create(name="Inventory", permissions=["inventory.manage"])
        employee_model.objects.create(user=self.employee, profile=profile)
        self.customer = User.objects.create_user(
            email="customer@example.com",
            password="Password123!",
            first_name="Some",
            last_name="Customer",
            role="customer",
        )

        self.category = Category.objects.create(
            name="Papelería y Suministros",
            slug="stationery",
        )
        self.product = Product.objects.create(
            name="Notebook",
            slug="notebook",
            category=self.category,
            product_type=Product.ProductType.PHYSICAL,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            name="Default",
            description="",
            variantnumber=1,
            slug="notebook-default",
            sku="SKU-001",
            selling_price=Decimal("100.00"),
            tax_rate=Decimal("18.00"),
        )

        # Seed an initial balance of 10 units for this variant.
        StockMovement_model.objects.create(
            product_variant=self.variant,
            movement_type="initial_inventory",
            quantity=10,
            balance=10,
        )

        self.url = reverse("api:stock-movement-decrease")

    def test_requires_authentication(self):
        response = self.client.post(
            self.url,
            {"sku": self.variant.sku, "quantity": 1, "reason": "Producto dañado"},
            format="json",
        )
        # Session auth (no JWT) has no WWW-Authenticate challenge, so DRF
        # returns 403 rather than 401 for unauthenticated requests here.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rejects_non_employee(self):
        self.client.force_authenticate(self.customer)
        response = self.client.post(
            self.url,
            {"sku": self.variant.sku, "quantity": 1, "reason": "Producto dañado"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_decreases_stock_and_records_who_and_why(self):
        self.client.force_authenticate(self.employee)
        response = self.client.post(
            self.url,
            {"sku": self.variant.sku, "quantity": 4, "reason": "Producto dañado"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data["data"]
        self.assertEqual(data["movement_type"], "manual_decrease")
        self.assertEqual(data["quantity"], 4)
        self.assertEqual(data["balance"], 6)
        self.assertEqual(data["stock_decrease"]["reason"], "Producto dañado")
        self.assertEqual(data["stock_decrease"]["decreased_by"]["email"], self.employee.email)

        movement = StockMovement_model.objects.get(id=data["id"])
        self.assertEqual(movement.balance, 6)

        decrease = StockDecrease_model.objects.get(stock_movement=movement)
        self.assertEqual(decrease.decreased_by, self.employee)
        self.assertEqual(decrease.reason, "Producto dañado")

    def test_rejects_decrease_below_zero_balance(self):
        self.client.force_authenticate(self.employee)
        response = self.client.post(
            self.url,
            {"sku": self.variant.sku, "quantity": 999, "reason": "Producto dañado"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(StockDecrease_model.objects.exists())
        # Only the initial_inventory movement from setUp should exist.
        self.assertEqual(StockMovement_model.objects.count(), 1)

    def test_requires_reason(self):
        self.client.force_authenticate(self.employee)
        response = self.client.post(
            self.url,
            {"sku": self.variant.sku, "quantity": 1, "reason": ""},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unknown_sku_returns_404(self):
        self.client.force_authenticate(self.employee)
        response = self.client.post(
            self.url,
            {"sku": "DOES-NOT-EXIST", "quantity": 1, "reason": "Producto dañado"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
