from django.urls import path

from holistic_data_presentation.views import (
    TherapistRateListView,
    OrgTherapistRateListView,
    TotalAllTherapistListView,
    TotalTherapistListView,
    OrgTotalTherapistListView,
)

urlpatterns = [
    path(
        'total-therapists/',
        TotalTherapistListView.as_view(),
        name='total-therapists'
    ),
    path(
        'total-therapists/all/',
        TotalAllTherapistListView.as_view(),
        name='total-all-therapists'
    ),
    path(
        'organizations/<int:id>/total-therapists/',
        OrgTotalTherapistListView.as_view(),
        name='total-therapists-per-organization'
    ),
    path(
        'rates/',
        TherapistRateListView.as_view(),
        name='rates'
    ),
    path(
        'organizations/<int:id>/rates/',
        OrgTherapistRateListView.as_view(),
        name='rates-per-organization'
    ),
]
