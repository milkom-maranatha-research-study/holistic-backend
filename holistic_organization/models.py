from django.db import models
from django.db.models import F


class Organization(models.Model):
    name = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        default=''
    )


class TherapistOrganization(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE
    )
    date_joined = models.DateField()

    class Meta:
        unique_together = (
            ('id', 'organization'),
        )


class TherapistInteractionQuerySet(models.QuerySet):

    def annotate_organization_id(self):
        """
        Annotates the `self` queryset with `organization_id`.
        """
        return self.annotate(organization_id=F('therapist__organization_id'))

    def annotate_organization_date_joined(self):
        """
        Annotates the `self` queryset with `organization_date_joined`.
        """
        return self.annotate(organization_date_joined=F('therapist__date_joined'))

    def join_with_organization(self):
        """
        Annotates the `self` queryset with `organization_id` and `organization_date_joined`.
        """
        return self.annotate_organization_id().annotate_organization_date_joined()


class TherapistInteraction(models.Model):
    therapist = models.ForeignKey(
        TherapistOrganization,
        on_delete=models.CASCADE
    )
    interaction_id = models.PositiveIntegerField()
    chat_count = models.PositiveIntegerField()
    call_count = models.PositiveIntegerField()
    interaction_date = models.DateField()

    objects = TherapistInteractionQuerySet.as_manager()

    class Meta:
        unique_together = (
            ('therapist', 'interaction_date', 'interaction_id'),
        )
