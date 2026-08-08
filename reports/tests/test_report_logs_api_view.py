# reports/tests/test_report_logs_api_view.py
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Profile, employee_model
from reports.models import ReportLog

User = get_user_model()


class ReportLogsAPITests(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            email="admin@example.com",
            password="Password123!",
            first_name="Root",
            last_name="Admin",
        )

        profile = Profile.objects.create(name="Reportes", permissions=["reports.create", "orders.view"])
        self.employee = User.objects.create_user(
            email="employee@example.com",
            password="Password123!",
            first_name="Regular",
            last_name="Employee",
            role="employee",
        )
        employee_model.objects.create(user=self.employee, profile=profile)

        self.older_log = ReportLog.objects.create(
            generated_by=self.employee, report_type="orders", format="csv",
            filters={"status": "pending"}, row_count=3,
        )
        self.newer_log = ReportLog.objects.create(
            generated_by=self.employee, report_type="orders", format="pdf",
            filters={}, row_count=5,
        )

        self.url = reverse("api:admin-reports-logs")

    def test_rejects_non_superuser_even_with_reports_create(self):
        self.client.force_authenticate(self.employee)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_allows_superuser(self):
        self.client.force_authenticate(self.superuser)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total"], 2)

        rows = response.data["data"]
        self.assertEqual(rows[0]["id"], self.newer_log.id)  # ordered -created_at
        self.assertEqual(rows[1]["id"], self.older_log.id)

        first = rows[0]
        self.assertEqual(first["generated_by"]["email"], self.employee.email)
        self.assertEqual(first["report_type"], "orders")
        self.assertEqual(first["format"], "pdf")
        self.assertEqual(first["row_count"], 5)
