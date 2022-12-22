from django.contrib import admin


from holistic_data_presentation.models import (
    NumberOfTherapist,
    OrganizationRate
)


@admin.register(NumberOfTherapist)
class NumberOfTherapistAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'organization',
        'period_type',
        'start_date',
        'end_date',
        'is_active',
        'value',
    )
    list_filter = (
        'organization',
        'period_type',
        'start_date',
        'end_date',
    )
    list_per_page = 25
    raw_id_fields = ('organization',)
    search_fields = ('organization__name',)


@admin.register(OrganizationRate)
class OrganizationRateAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'organization',
        'period_type',
        'start_date',
        'end_date',
        'type',
        'rate_value',
    )
    list_filter = (
        'organization',
        'type',
        'period_type',
        'start_date',
        'end_date',
    )
    list_per_page = 25
    raw_id_fields = ('organization',)
    search_fields = ('organization__name',)
