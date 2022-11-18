from django.contrib import admin


from holistic_data_presentation.models import (
    NumberOfTherapist,
    ChurnRetentionRate
)


@admin.register(NumberOfTherapist)
class NumberOfTherapistAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'organization',
        'start_date',
        'end_date',
        'is_active',
        'value',
    )
    list_filter = (
        'organization',
        'start_date',
        'end_date',
    )
    list_per_page = 25
    raw_id_fields = ('organization',)
    search_fields = ('organization__name',)


@admin.register(ChurnRetentionRate)
class ChurnRetentionRateAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'organization',
        'start_date',
        'end_date',
        'type',
        'rate_value',
    )
    list_filter = (
        'type',
        'organization',
        'start_date',
        'end_date',
    )
    list_per_page = 25
    raw_id_fields = ('organization',)
    search_fields = ('organization__name',)
