from django.urls import path

from holistic_organization.views import (
    InteractionExportView,
    InteractionSyncView,
    OrganizationListView,
    OrganizationSyncView,
    TherapistExportView,
    TherapistSyncView,
)

urlpatterns = [
    path(
        'organizations/',
        OrganizationListView.as_view(),
        name='organizations'
    ),
    path(
        'therapists/export/',
        TherapistExportView.as_view(),
        name='export-all-therapists'
    ),
    path(
        'interactions/export/',
        InteractionExportView.as_view(),
        name='export-all-interactions'
    ),
    path(
        'sync/organizations/',
        OrganizationSyncView.as_view(),
        name='sync-organizations'
    ),
    path(
        'sync/organizations/<int:id>/therapists/',
        TherapistSyncView.as_view(),
        name='sync-therapists-organization'
    ),
    path(
        'sync/therapists/<str:id>/interactions/',
        InteractionSyncView.as_view(),
        name='sync-therapist-interactions'
    ),
]
