from django.urls import path

from holistic_organization.views import (
    OrganizationListView,
    TherapistListView,
    InteractionListView,
    OrganizationSyncView,
    TherapistSyncView,
    InteractionSyncView,
)

urlpatterns = [
    path(
        'organizations/',
        OrganizationListView.as_view(),
        name='organizations'
    ),
    path(
        'therapists/export/',
        TherapistListView.as_view(),
        name='export-all-therapists'
    ),
    path(
        'interactions/export/',
        InteractionListView.as_view(),
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
