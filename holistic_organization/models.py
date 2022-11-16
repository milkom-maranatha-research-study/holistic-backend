from django.db import models


class Organization(models.Model):
    name = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        default=''
    )


class TherapistOrganization(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE
    )
    therapist_id = models.CharField(max_length=32)
    date_joined = models.DateField()

    class Meta:
        unique_together = (
            ('organization', 'therapist_id'),
        )


class TherapistInteraction(models.Model):
    therapist_id = models.CharField(max_length=32)
    interaction_date = models.DateField()
    chat_count = models.PositiveIntegerField()
    call_count = models.PositiveIntegerField()
