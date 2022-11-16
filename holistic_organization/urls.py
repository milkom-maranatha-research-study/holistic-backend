from django.urls import path

from holistic_organization.views import (
    OrganizationSyncView,
    TherapistOrganizationSyncView,
    TherapistInteractionSyncView,
)

urlpatterns = [
    path(
        'organizations/sync/',
        OrganizationSyncView.as_view(),
        name='sync-organizations'
    ),
    path(
        'therapists-organizations/sync/',
        TherapistOrganizationSyncView.as_view(),
        name='sync-therapists-organizations'
    ),
    path(
        'therapists-interactions/sync/',
        TherapistInteractionSyncView.as_view(),
        name='sync-therapists-interactions'
    ),
]
