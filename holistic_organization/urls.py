from django.urls import path

from holistic_organization.views import (
    OrganizationListView,
    OrganizationSyncView,
    TherapistOrganizationSyncView,
    TherapistInteractionSyncView,
)

urlpatterns = [
    path(
        'organizations/',
        OrganizationListView.as_view(),
        name='organizations'
    ),
    path(
        'sync/organizations/',
        OrganizationSyncView.as_view(),
        name='sync-organizations'
    ),
    path(
        'sync/organizations/<int:id>/therapists/',
        TherapistOrganizationSyncView.as_view(),
        name='sync-organization-therapists'
    ),
    path(
        'sync/organizations/therapists/<str:id>/interactions/',
        TherapistInteractionSyncView.as_view(),
        name='sync-therapist-interactions'
    ),
]
