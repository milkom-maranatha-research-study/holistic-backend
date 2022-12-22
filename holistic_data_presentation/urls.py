from django.urls import path

from holistic_data_presentation.views import (
    TotalTherapistListView,
    TotalTherapistDetailView,
    OrganizationRateListView,
    OrganizationRateDetailView,
)

urlpatterns = [
    path(
        'presentation/organizations/number-of-therapists/',
        TotalTherapistListView.as_view(),
        name='number-of-therapists-in-organizations'
    ),
    path(
        'presentation/organizations/<int:id>/number-of-therapists/',
        TotalTherapistDetailView.as_view(),
        name='number-of-therapists-per-organization'
    ),
    path(
        'presentation/organizations/rates/',
        OrganizationRateListView.as_view(),
        name='rates-organizations'
    ),
    path(
        'presentation/organizations/<int:id>/rates/',
        OrganizationRateDetailView.as_view(),
        name='rates-per-organization'
    ),
]
