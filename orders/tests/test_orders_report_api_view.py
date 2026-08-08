# orders/tests/test_orders_report_api_view.py
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Profile, employee_model
from orders.models import Order, OrderItem
from products.default.models import Category, Product, ProductVariant
from reports.models import ReportLog

User = get_user_model()


class AdminOrdersReportAPITests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            email="customer@example.com",
            password="Password123!",
            first_name="Jane",
            last_name="Doe",
            role="customer",
        )

        category = Category.objects.create(name="Papelería", slug="papeleria")
        product = Product.objects.create(
            name="Cuaderno",
            slug="cuaderno",
            category=category,
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

        self.pending_order = Order.objects.create(customer=self.customer, status="pending")
        OrderItem.objects.create(
            order=self.pending_order, product=self.variant, quantity=2,
            price_per_item=100.0, tax_amount=18.0,
        )
        self.fulfilled_order = Order.objects.create(customer=self.customer, status="fulfilled")
        OrderItem.objects.create(
            order=self.fulfilled_order, product=self.variant, quantity=1,
            price_per_item=100.0, tax_amount=18.0,
        )

        self.report_url = reverse("api:admin-orders-report")
        self.list_url = reverse("api:admin-orders-list")

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

    def test_requires_orders_view_and_reports_create(self):
        neither = self._make_employee([])
        only_orders_view = self._make_employee(["orders.view"])
        only_reports_create = self._make_employee(["reports.create"])
        both = self._make_employee(["orders.view", "reports.create"])

        for user in (neither, only_orders_view, only_reports_create):
            self.client.force_authenticate(user)
            response = self.client.get(self.report_url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(both)
        response = self.client.get(self.report_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pdf_export_returns_downloadable_file(self):
        employee = self._make_employee(["orders.view", "reports.create"])
        self.client.force_authenticate(employee)

        response = self.client.get(self.report_url, {"report_format": "pdf"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("attachment;", response["Content-Disposition"])
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_csv_export_returns_downloadable_file(self):
        employee = self._make_employee(["orders.view", "reports.create"])
        self.client.force_authenticate(employee)

        response = self.client.get(self.report_url, {"report_format": "csv"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("attachment;", response["Content-Disposition"])
        body = response.content.decode("utf-8-sig")
        self.assertIn("Cliente", body)
        self.assertEqual(body.strip().count("\n") + 1, 3)  # header + 2 orders

    def test_filters_match_admin_orders_list(self):
        employee = self._make_employee(["orders.view", "reports.create"])
        self.client.force_authenticate(employee)

        list_response = self.client.get(self.list_url, {"status": "pending", "limit": 50})
        report_response = self.client.get(
            self.report_url, {"status": "pending", "report_format": "csv"}
        )

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(report_response.status_code, status.HTTP_200_OK)

        listed_ids = {row["id"] for row in list_response.data["data"]}
        self.assertEqual(listed_ids, {self.pending_order.id})

        report_body = report_response.content.decode("utf-8-sig")
        self.assertIn(str(self.pending_order.id), report_body)
        self.assertNotIn(f"{self.fulfilled_order.id},", report_body)

    def test_creates_report_log_entry(self):
        employee = self._make_employee(["orders.view", "reports.create"])
        self.client.force_authenticate(employee)

        self.assertEqual(ReportLog.objects.count(), 0)

        response = self.client.get(self.report_url, {"status": "pending", "report_format": "csv"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        log = ReportLog.objects.get()
        self.assertEqual(log.generated_by, employee)
        self.assertEqual(log.report_type, "orders")
        self.assertEqual(log.format, "csv")
        self.assertEqual(log.row_count, 1)
        self.assertEqual(log.filters.get("status"), "pending")
