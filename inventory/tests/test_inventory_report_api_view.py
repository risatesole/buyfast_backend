# inventory/tests/test_inventory_report_api_view.py
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Profile, employee_model
from inventory.models import StockMovement_model
from products.default.models import Category, Product, ProductVariant
from reports.models import ReportLog

User = get_user_model()


class InventoryReportAPITestsBase(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Papelería", slug="papeleria")
        product = Product.objects.create(
            name="Cuaderno",
            slug="cuaderno",
            category=self.category,
            product_type=Product.ProductType.PHYSICAL,
        )
        self.variant = ProductVariant.objects.create(
            product=product,
            name="Default",
            description="",
            variantnumber=1,
            slug="cuaderno-default",
            sku="SKU-CUAD-001",
            selling_price=Decimal("100.00"),
            tax_rate=Decimal("18.00"),
        )
        StockMovement_model.objects.create(
            product_variant=self.variant, movement_type="initial_inventory", quantity=5, balance=5,
        )
        StockMovement_model.objects.create(
            product_variant=self.variant, movement_type="purchase_entry", quantity=20, balance=25,
        )

    def _make_employee(self, permissions):
        profile = Profile.objects.create(name=f"Profile-{'-'.join(permissions) or 'none'}", permissions=permissions)
        employee = User.objects.create_user(
            email=f"{'-'.join(permissions) or 'none'}@example.com",
            password="Password123!",
            first_name="Employee",
            last_name="Tester",
            role="employee",
        )
        employee_model.objects.create(user=employee, profile=profile)
        return employee


class AdminInventoryStockReportAPITests(InventoryReportAPITestsBase):
    def setUp(self):
        super().setUp()
        self.report_url = reverse("api:admin-inventory-stock-report")
        self.list_url = reverse("api:admin-inventory-products-list")

    def test_requires_inventory_view_and_reports_create(self):
        neither = self._make_employee([])
        only_inventory_view = self._make_employee(["inventory.view"])
        only_reports_create = self._make_employee(["reports.create"])
        both = self._make_employee(["inventory.view", "reports.create"])

        for user in (neither, only_inventory_view, only_reports_create):
            self.client.force_authenticate(user)
            response = self.client.get(self.report_url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(both)
        response = self.client.get(self.report_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pdf_and_csv_exports(self):
        employee = self._make_employee(["inventory.view", "reports.create"])
        self.client.force_authenticate(employee)

        pdf_response = self.client.get(self.report_url, {"report_format": "pdf"})
        self.assertEqual(pdf_response.status_code, status.HTTP_200_OK)
        self.assertEqual(pdf_response["Content-Type"], "application/pdf")
        self.assertTrue(pdf_response.content.startswith(b"%PDF"))

        csv_response = self.client.get(self.report_url, {"report_format": "csv"})
        self.assertEqual(csv_response.status_code, status.HTTP_200_OK)
        self.assertEqual(csv_response["Content-Type"], "text/csv")
        body = csv_response.content.decode("utf-8-sig")
        self.assertIn(self.variant.sku, body)
        self.assertIn("Papelería", body)

    def test_filters_match_admin_inventory_list(self):
        employee = self._make_employee(["inventory.view", "reports.create"])
        self.client.force_authenticate(employee)

        # This variant's balance is 25 (5 initial + 20 purchase), which falls
        # in the "medium_stock" bucket (10 < quantity <= 50).
        list_response = self.client.get(self.list_url, {"inventory_status": "medium_stock", "limit": 50})
        report_response = self.client.get(
            self.report_url, {"inventory_status": "medium_stock", "report_format": "csv"}
        )

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(report_response.status_code, status.HTTP_200_OK)

        listed_skus = {row["sku"] for row in list_response.data["results"]}
        self.assertEqual(listed_skus, {self.variant.sku})

        report_body = report_response.content.decode("utf-8-sig")
        self.assertIn(self.variant.sku, report_body)

    def test_creates_report_log_entry(self):
        employee = self._make_employee(["inventory.view", "reports.create"])
        self.client.force_authenticate(employee)

        response = self.client.get(self.report_url, {"category": "papeleria", "report_format": "csv"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        log = ReportLog.objects.get()
        self.assertEqual(log.generated_by, employee)
        self.assertEqual(log.report_type, "inventory_stock")
        self.assertEqual(log.format, "csv")
        self.assertEqual(log.row_count, 1)
        self.assertEqual(log.filters.get("category"), "papeleria")


class AdminInventoryMovementsReportAPITests(InventoryReportAPITestsBase):
    def setUp(self):
        super().setUp()
        self.report_url = reverse("api:admin-inventory-movements-report")
        self.list_url = reverse("api:stock-movement-list")

    def test_requires_inventory_view_and_reports_create(self):
        neither = self._make_employee([])
        both = self._make_employee(["inventory.view", "reports.create"])

        self.client.force_authenticate(neither)
        response = self.client.get(self.report_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(both)
        response = self.client.get(self.report_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_csv_export_and_movement_type_filter(self):
        employee = self._make_employee(["inventory.view", "reports.create"])
        self.client.force_authenticate(employee)

        response = self.client.get(
            self.report_url, {"movement_type": "purchase_entry", "report_format": "csv"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.content.decode("utf-8-sig")
        self.assertIn("Entrada por Compra", body)
        self.assertNotIn("Inventario Inicial", body)

    def test_creates_report_log_entry(self):
        employee = self._make_employee(["inventory.view", "reports.create"])
        self.client.force_authenticate(employee)

        response = self.client.get(self.report_url, {"report_format": "pdf"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        log = ReportLog.objects.get()
        self.assertEqual(log.report_type, "inventory_movements")
        self.assertEqual(log.format, "pdf")
        self.assertEqual(log.row_count, 2)
