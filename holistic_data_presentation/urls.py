from django.urls import path

from holistic_data_presentation.views import (
    TotalTherapistListView,
    TotalTherapistPerOrganizationListView,
    ChurnRetentionRateListView,
    ChurnRetentionRatePerOrganizationListView,
)

urlpatterns = [
    path(
        'data-presentation/number-of-therapists/',
        TotalTherapistListView.as_view(),
        name='data-presentation-total-therapists'
    ),
    path(
        'data-presentation/organizations/<int:id>/number-of-therapists/',
        TotalTherapistPerOrganizationListView.as_view(),
        name='data-presentation-total-therapists-per-org'
    ),
    path(
        'data-presentation/churn-retention-rates/',
        ChurnRetentionRateListView.as_view(),
        name='data-presentation-churn-retention-rates'
    ),
    path(
        'data-presentation/organizations/<int:id>/churn-retention-rates/',
        ChurnRetentionRatePerOrganizationListView.as_view(),
        name='data-presentation-churn-retention-rates-per-org'
    ),
]
