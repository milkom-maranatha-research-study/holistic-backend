from django.db import models
from django.db.models import OuterRef, Subquery


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
        indexes = [
            models.Index(fields=['organization_id', 'therapist_id']),
        ]


class TherapistInteractionQuerySet(models.QuerySet):

    def annotate_organization_id(self):
        """
        Annotates the `self` queryset with `organization_id`.
        """
        queryset = TherapistOrganization.objects.filter(therapist_id=OuterRef('therapist_id'))
        return self.annotate(organization_id=Subquery(queryset.values('organization')[:1]))

    def annotate_organization_date_joined(self):
        """
        Annotates the `self` queryset with `organization_date_joined`.
        """
        queryset = TherapistOrganization.objects.filter(therapist_id=OuterRef('therapist_id'))
        return self.annotate(organization_date_joined=Subquery(queryset.values('date_joined')[:1]))

    def join_with_organization(self):
        """
        Annotates the `self` queryset with `organization_id` and `organization_date_joined`.
        """
        return self.annotate_organization_id().annotate_organization_date_joined()


class TherapistInteraction(models.Model):
    interaction_id = models.PositiveIntegerField()
    therapist_id = models.CharField(max_length=32)
    chat_count = models.PositiveIntegerField()
    call_count = models.PositiveIntegerField()
    interaction_date = models.DateField()

    objects = TherapistInteractionQuerySet.as_manager()

    class Meta:
        unique_together = (
            ('interaction_id', 'therapist_id', 'interaction_date'),
        )
        indexes = [
            models.Index(fields=['id', 'therapist_id']),
            models.Index(fields=['therapist_id', 'interaction_date']),
        ]
