from django.db import models

from holistic_organization.models import Organization


class NumberOfTherapist(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE
    )

    start_date = models.DateField()
    end_date = models.DateField()

    is_active = models.BooleanField(default=False)
    value = models.PositiveIntegerField()


class ChurnRetentionRate(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE
    )

    TYPE_CHURN_RATE = 'churn_rate'
    TYPE_RETENTION_RATE = 'retention_rate'
    TYPE_CHOICES = (
        (TYPE_CHURN_RATE, 'Churn Rate'),
        (TYPE_RETENTION_RATE, 'Retention Rate'),
    )
    type = models.CharField(
        max_length=16,
        choices=TYPE_CHOICES
    )

    start_date = models.DateField()
    end_date = models.DateField()

    rate_value = models.FloatField()
