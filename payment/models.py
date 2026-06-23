from django.db import models


class PaymentProvider(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = "payment_provider"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_default:
            # Unset any other default before saving this one
            PaymentProvider.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class PaymentProviderTransaction(models.Model):
    payment_provider = models.ForeignKey(
        PaymentProvider,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reference_document = models.CharField(max_length=255)
    amount = models.FloatField()
    tax = models.FloatField(default=0)

    class Meta:
        db_table = "payment_provider_transactions"

    def __str__(self):
        return self.reference_document