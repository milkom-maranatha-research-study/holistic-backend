from django.urls import path

from holistic_data_presentation.views import (
    AllTimeNumberOfTherapistListView,
    NumberOfTherapistListView,
    NumberOfTherapistDetailView,
    AllTimeOrganizationRateListView,
    OrganizationRateListView,
    OrganizationRateDetailView,
)

urlpatterns = [
    path(
        'number-of-therapists/',
        NumberOfTherapistListView.as_view(),
        name='number-of-therapists'
    ),
    path(
        'number-of-therapists/all-time/',
        AllTimeNumberOfTherapistListView.as_view(),
        name='all-time-number-of-therapists'
    ),
    path(
        'organizations/<int:id>/number-of-therapists/',
        NumberOfTherapistDetailView.as_view(),
        name='number-of-therapists-per-organization'
    ),
    path(
        'rates/',
        OrganizationRateListView.as_view(),
        name='rates'
    ),
    path(
        'rates/all-time/',
        AllTimeOrganizationRateListView.as_view(),
        name='all-time-rates'
    ),
    path(
        'organizations/<int:id>/rates/',
        OrganizationRateDetailView.as_view(),
        name='rates-per-organization'
    ),
]
