from django.urls import path

from holistic_data_presentation.views import (
    TherapistRateInOrgListView,
    TherapistRateListView,
    TotalTherapistInOrgListView,
    TotalTherapistListView,
)

urlpatterns = [
    path(
        'total-therapists/',
        TotalTherapistListView.as_view(),
        name='total-therapists'
    ),
    path(
        'organizations/<int:id>/total-therapists/',
        TotalTherapistInOrgListView.as_view(),
        name='total-therapists-per-organization'
    ),
    path(
        'rates/',
        TherapistRateListView.as_view(),
        name='rates'
    ),
    path(
        'organizations/<int:id>/rates/',
        TherapistRateInOrgListView.as_view(),
        name='rates-per-organization'
    ),
]
