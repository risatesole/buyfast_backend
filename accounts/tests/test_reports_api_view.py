# accounts/tests/test_reports_api_view.py
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Profile, employee_model
from orders.models import Order
from reports.models import ReportLog

User = get_user_model()


class ReportsAPITestsBase(APITestCase):
    def _make_employee(self, permissions, position="store_manager"):
        profile = Profile.objects.create(
            name=f"Profile-{'-'.join(permissions) or 'none'}-{position}", permissions=permissions
        )
        employee = User.objects.create_user(
            email=f"{'-'.join(permissions) or 'none'}-{position}@example.com",
            password="Password123!",
            first_name="Employee",
            last_name="Tester",
            role="employee",
        )
        employee_model.objects.create(user=employee, profile=profile, position=position)
        return employee, profile


class AdminEmployeesReportAPITests(ReportsAPITestsBase):
    def setUp(self):
        self.report_url = reverse("api:admin-employees-report")

    def test_requires_employees_view_and_reports_create(self):
        neither, _ = self._make_employee([])
        only_view, _ = self._make_employee(["employees.view"])
        only_create, _ = self._make_employee(["reports.create"])
        both, _ = self._make_employee(["employees.view", "reports.create"])

        for user in (neither, only_view, only_create):
            self.client.force_authenticate(user)
            response = self.client.get(self.report_url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(both)
        response = self.client.get(self.report_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_position_filter(self):
        reporter, _ = self._make_employee(["employees.view", "reports.create"], position="finance")
        _, finance_profile = self._make_employee(["employees.view"], position="finance")
        self._make_employee(["employees.view"], position="logistics")

        self.client.force_authenticate(reporter)
        response = self.client.get(self.report_url, {"position": "finance", "report_format": "csv"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.content.decode("utf-8-sig")
        self.assertIn("Finanzas", body)
        self.assertNotIn("Logística", body)

    def test_profile_filter(self):
        reporter, reporter_profile = self._make_employee(["employees.view", "reports.create"])
        _, other_profile = self._make_employee(["employees.view"])

        self.client.force_authenticate(reporter)
        response = self.client.get(
            self.report_url, {"profile": str(other_profile.id), "report_format": "csv"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.content.decode("utf-8-sig")
        self.assertIn(other_profile.name, body)
        self.assertNotIn(reporter_profile.name, body)

    def test_pdf_and_csv_exports(self):
        reporter, _ = self._make_employee(["employees.view", "reports.create"])
        self.client.force_authenticate(reporter)

        pdf_response = self.client.get(self.report_url, {"report_format": "pdf"})
        self.assertEqual(pdf_response.status_code, status.HTTP_200_OK)
        self.assertEqual(pdf_response["Content-Type"], "application/pdf")
        self.assertTrue(pdf_response.content.startswith(b"%PDF"))

        csv_response = self.client.get(self.report_url, {"report_format": "csv"})
        self.assertEqual(csv_response.status_code, status.HTTP_200_OK)
        self.assertEqual(csv_response["Content-Type"], "text/csv")

    def test_creates_report_log_entry(self):
        reporter, _ = self._make_employee(["employees.view", "reports.create"])
        self.client.force_authenticate(reporter)

        response = self.client.get(self.report_url, {"position": "store_manager", "report_format": "pdf"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        log = ReportLog.objects.get()
        self.assertEqual(log.generated_by, reporter)
        self.assertEqual(log.report_type, "employees")
        self.assertEqual(log.format, "pdf")
        self.assertEqual(log.filters.get("position"), "store_manager")


class AdminCustomersReportAPITests(ReportsAPITestsBase):
    def setUp(self):
        self.report_url = reverse("api:admin-customers-report")

    def _make_customer(self, institution_member=False, order_count=0):
        customer = User.objects.create_user(
            email=f"customer-{User.objects.count()}@example.com",
            password="Password123!",
            first_name="Cliente",
            last_name="Tester",
            role="customer",
            institution_member=institution_member,
        )
        for _ in range(order_count):
            Order.objects.create(customer=customer)
        return customer

    def test_requires_customers_view_and_reports_create(self):
        neither, _ = self._make_employee([])
        only_view, _ = self._make_employee(["customers.view"])
        only_create, _ = self._make_employee(["reports.create"])
        both, _ = self._make_employee(["customers.view", "reports.create"])

        for user in (neither, only_view, only_create):
            self.client.force_authenticate(user)
            response = self.client.get(self.report_url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(both)
        response = self.client.get(self.report_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_institution_member_filter(self):
        reporter, _ = self._make_employee(["customers.view", "reports.create"])
        member = self._make_customer(institution_member=True)
        self._make_customer(institution_member=False)

        self.client.force_authenticate(reporter)
        response = self.client.get(
            self.report_url, {"institution_member": "true", "report_format": "csv"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.content.decode("utf-8-sig")
        self.assertIn(member.email, body)
        self.assertEqual(body.strip().count("\n") + 1, 2)  # header + 1 matching customer

    def test_purchase_count_filter(self):
        reporter, _ = self._make_employee(["customers.view", "reports.create"])
        frequent_buyer = self._make_customer(order_count=3)
        self._make_customer(order_count=0)

        self.client.force_authenticate(reporter)
        response = self.client.get(
            self.report_url, {"min_purchases": "1", "report_format": "csv"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.content.decode("utf-8-sig")
        self.assertIn(frequent_buyer.email, body)
        self.assertIn("3", body)

    def test_pdf_and_csv_exports(self):
        reporter, _ = self._make_employee(["customers.view", "reports.create"])
        self._make_customer()
        self.client.force_authenticate(reporter)

        pdf_response = self.client.get(self.report_url, {"report_format": "pdf"})
        self.assertEqual(pdf_response.status_code, status.HTTP_200_OK)
        self.assertEqual(pdf_response["Content-Type"], "application/pdf")
        self.assertTrue(pdf_response.content.startswith(b"%PDF"))

        csv_response = self.client.get(self.report_url, {"report_format": "csv"})
        self.assertEqual(csv_response.status_code, status.HTTP_200_OK)
        self.assertEqual(csv_response["Content-Type"], "text/csv")

    def test_creates_report_log_entry(self):
        reporter, _ = self._make_employee(["customers.view", "reports.create"])
        self.client.force_authenticate(reporter)

        response = self.client.get(
            self.report_url, {"institution_member": "false", "report_format": "csv"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        log = ReportLog.objects.get()
        self.assertEqual(log.generated_by, reporter)
        self.assertEqual(log.report_type, "customers")
        self.assertEqual(log.format, "csv")
        self.assertEqual(log.filters.get("institution_member"), "false")
