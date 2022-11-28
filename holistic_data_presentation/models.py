from django.db import models

from holistic_organization.models import Organization


class NumberOfTherapist(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE
    )

    TYPE_WEEKLY = 'weekly'
    TYPE_MONTHLY = 'monthly'
    TYPE_YEARLY = 'yearly'
    PERIOD_CHOICES = (
        (TYPE_WEEKLY, 'Weekly'),
        (TYPE_MONTHLY, 'Monthly'),
        (TYPE_YEARLY, 'Yearly'),
    )
    period_type = models.CharField(
        max_length=8,
        choices=PERIOD_CHOICES
    )

    start_date = models.DateField()
    end_date = models.DateField()

    is_active = models.BooleanField(default=False)
    value = models.PositiveIntegerField()

    class Meta:
        unique_together = (
            'organization',
            'start_date',
            'end_date',
            'period_type',
            'is_active',
        )


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

    TYPE_WEEKLY = 'weekly'
    TYPE_MONTHLY = 'monthly'
    TYPE_YEARLY = 'yearly'
    PERIOD_CHOICES = (
        (TYPE_WEEKLY, 'Weekly'),
        (TYPE_MONTHLY, 'Monthly'),
        (TYPE_YEARLY, 'Yearly'),
    )
    period_type = models.CharField(
        max_length=8,
        choices=PERIOD_CHOICES
    )

    start_date = models.DateField()
    end_date = models.DateField()

    rate_value = models.FloatField()

    class Meta:
        unique_together = (
            'organization',
            'type',
            'start_date',
            'end_date',
            'period_type',
        )
