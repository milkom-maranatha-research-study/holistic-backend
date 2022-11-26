from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework.exceptions import ValidationError

from holistic_data_presentation.models import (
    NumberOfTherapist,
    ChurnRetentionRate,
)


class BaseDataPresentationFilter(filters.FilterSet):

    period_type = filters.CharFilter(
        method='filter_by_period_type'
    )

    period = filters.DateFromToRangeFilter(
        method='filter_by_period'
    )

    @property
    def qs(self):

        period_after = self.data.get('period_after')
        period_before = self.data.get('period_before')

        # If both `period_after` and `period_before` is None
        if period_after is None and period_before is None:
            return super().qs

        # If one of `period_after` or `period_before` is None
        elif period_after is None or period_before is None:
            raise ValidationError(
                '`period_after` and `period_before` parameter must be given together.'
            )

        return super().qs

    def filter_by_period(self, queryset, name, value):

        period_type = self.data.get('period_type')

        # If `period_type` is also provided, we need to `and`-ed it with the period filter
        # Otherwise, the period filtration won't work.
        if period_type:
            return self.filter_by_period_and_period_type(
                queryset, value.start, value.stop, period_type
            )

        return queryset.filter(
            Q(start_date__gte=value.start, start_date__lte=value.stop) |  # noqa: W504
            Q(end_date__gt=value.start, end_date__lte=value.stop)
        )

    def filter_by_period_type(self, queryset, name, value):

        period_after = self.data.get('period_after')
        period_before = self.data.get('period_before')

        if period_after and period_before:
            return self.filter_by_period_and_period_type(
                queryset, period_after, period_before, value
            )

        return queryset.filter(period_type=value)

    def filter_by_period_and_period_type(self, queryset, period_after, period_before, period_type):

        return queryset.filter(
            Q(period_type=period_type) &  # noqa: W504
            (
                Q(start_date__gte=period_after, start_date__lte=period_before) |  # noqa: W504
                Q(end_date__gt=period_after, end_date__lte=period_before)
            )
        )


class TotalTherapistFilter(BaseDataPresentationFilter):
    is_active = filters.BooleanFilter(
        field_name='is_active'
    )

    class Meta:
        model = NumberOfTherapist
        fields = ('is_active',)


class ChurnRetentionRateFilter(BaseDataPresentationFilter):
    type = filters.CharFilter(
        field_name='type'
    )

    class Meta:
        model = ChurnRetentionRate
        fields = ('type',)

