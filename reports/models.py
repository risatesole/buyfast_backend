from django.conf import settings
from django.db import models


class ReportLog(models.Model):
    """
    Audit trail of every report generated from the admin panel. report_type
    is a plain string (not an enum) so new report types (products, employees,
    customers, ...) can start logging without a migration.
    """

    FORMAT_CHOICES = [
        ("pdf", "PDF"),
        ("csv", "CSV"),
    ]

    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="report_logs",
    )
    report_type = models.CharField(max_length=50)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    filters = models.JSONField(default=dict, blank=True)
    row_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_report_log"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.report_type} report ({self.format}) by {self.generated_by}"
