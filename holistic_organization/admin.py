from django.contrib import admin


from holistic_organization.models import (
    Organization,
    TherapistOrganization,
    TherapistInteraction
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
    )
    list_per_page = 25


@admin.register(TherapistOrganization)
class TherapistOrganizationAdmin(admin.ModelAdmin):
    list_display = (
        'therapist_id',
        'organization',
        'date_joined',
    )
    list_per_page = 25
    raw_id_fields = ('organization',)


@admin.register(TherapistInteraction)
class TherapistInteractionAdmin(admin.ModelAdmin):
    list_display = (
        'therapist_id',
        'interaction_date',
        'chat_count',
        'call_count',
    )
    list_per_page = 25
