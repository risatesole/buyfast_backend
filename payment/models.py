from django.db import models


class PaymentProvider(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    added_at = models.DateTimeField()

    class Meta:
        db_table = "payment_provider"

    def __str__(self):
        return self.name


class PaymentProviderTransaction(models.Model):
    payment_provider = models.ForeignKey(
        PaymentProvider,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    created_at = models.DateTimeField()
    reference_document = models.CharField(max_length=255)
    amount = models.FloatField()
    tax = models.FloatField()

    class Meta:
        db_table = "payment_provider_transactions"

    def __str__(self):
        return self.reference_document
