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
    list_filter = ('id', 'name',)
    list_per_page = 25
    search_fields = ('name',)


@admin.register(TherapistOrganization)
class TherapistOrganizationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'organization',
        'date_joined',
    )
    list_filter = ('id', 'organization',)
    list_per_page = 25
    raw_id_fields = ('organization',)
    search_fields = (
        'id',
        'organization__name',
    )


@admin.register(TherapistInteraction)
class TherapistInteractionAdmin(admin.ModelAdmin):
    list_display = (
        'therapist',
        'interaction_date',
        'interaction_id',
        'chat_count',
        'call_count',
    )
    list_filter = ('therapist', 'interaction_date',)
    list_per_page = 25
    search_fields = ('therapist_id',)
