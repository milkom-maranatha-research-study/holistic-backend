from django.db import transaction
from rest_framework import serializers

from holistic_data_presentation.models import (
    TherapistRate,
    TotalTherapist,
)
from holistic_data_presentation.validators import (
    validate_weekly_period,
    validate_monthly_period,
    validate_yearly_period,
)


class BatchCreateSerializer(serializers.Serializer):
    rows_created = serializers.IntegerField()
    rows_updated = serializers.IntegerField(required=False)


class TotalTherapistSerializer(serializers.ModelSerializer):
    class Meta:
        model = TotalTherapist
        fields = (
            'period_type',
            'organization',
            'start_date',
            'end_date',
            'is_active',
            'value',
        )
        read_only = fields


class BaseTotalTherapistBatchDeserializer(serializers.ListSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.organization_id = None

    @transaction.atomic
    def create(self, list_total_thers):
        """
        We override this method to implement upsert the total therapists in batch.

        @param list_total_thers: Validated JSON Array that contains a list of total therapists.
        """
        existing_total_thers = self.get_existing_total_therapists()

        to_update_objects = self._get_objects_to_update(list_total_thers, existing_total_thers)
        to_create_objects = self._get_objects_to_create(list_total_thers, existing_total_thers)

        TotalTherapist.objects.bulk_update(to_update_objects, fields=['period_type', 'value'])
        rows_created = len(TotalTherapist.objects.bulk_create(to_create_objects))
        rows_updated = len(list_total_thers) - rows_created

        return {'rows_created': rows_created, 'rows_updated': rows_updated}

    def get_existing_total_therapists(self):
        """
        Returns the existing `TotalTherapist` objects based on that incoming `list_total_thers`.
        """
        raise NotImplementedError()

    def _get_objects_to_create(self, list_total_thers, existing_total_thers):
        """
        Returns a list of `TotalTherapist` objects that are going to be created in batch.

        @param list_total_thers: Validated JSON Array that contains a list of total therapists.
        @param existing_total_thers: Existing total therapists.
        """
        return [
            TotalTherapist(
                organization_id=self.organization_id,
                period_type=item['period_type'],
                start_date=item['start_date'],
                end_date=item['end_date'],
                is_active=item['is_active'],
                value=item['value']
            )
            for item in list_total_thers if self._is_new_item(item, existing_total_thers)
        ]

    def _is_new_item(self, item, existing_total_thers):
        """
        Returns `True` if that `item` doesn't exist
        in the list of existing existing total therapists.

        @param item: A dictionary that represents the total therapist within the payload data.
        @param existing_total_thers: Existing total therapists.
        """
        for total_ther in existing_total_thers:
            if bool(
                item['start_date'] == total_ther.start_date and
                item['end_date'] == total_ther.end_date and
                item['is_active'] == total_ther.is_active
            ):
                return False

        return True

    def _get_objects_to_update(self, list_total_thers, existing_total_thers):
        """
        Returns a list of `TotalTherapist` objects that are going to be updated in batch.

        @param list_total_thers: Validated JSON Array that contains a list of total therapists.
        @param existing_total_thers: Existing total therapists.
        """
        objects_to_update = []

        for item in list_total_thers:
            to_update = self._get_object_to_update(item, existing_total_thers)

            if to_update is None:
                # That `item` doesn't exists,
                # skip it from the update candidates.
                continue

            item, num_of_ther = list(to_update)
            num_of_ther.value = item['value']

            objects_to_update.append(num_of_ther)

        return objects_to_update

    def _get_object_to_update(self, item, existing_total_thers):
        """
        Returns a pair of (`item`, `TotalTherapist`)
        if the `item` exists on the list of existing total therapists.

        @param item: A dictionary that represents the Therapist within the payload data.
        @param existing_total_thers: Existing total therapists.
        """
        for total_ther in existing_total_thers:
            if bool(
                item['start_date'] == total_ther.start_date and
                item['end_date'] == total_ther.end_date and
                item['is_active'] == total_ther.is_active
            ):
                return (item, total_ther)

        return None


class TotalTherapistBatchDeserializer(BaseTotalTherapistBatchDeserializer):

    def get_existing_total_therapists(self):
        """
        Returns the existing `TotalTherapist` objects in Niceday.
        """
        return TotalTherapist.objects.filter(organization__isnull=True)


class TotalTherapistInOrgBatchDeserializer(BaseTotalTherapistBatchDeserializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.organization_id = self.context['organization_id']

    def get_existing_total_therapists(self):
        """
        Returns the existing `TotalTherapist` objects in the Organization.
        """
        return TotalTherapist.objects.filter(organization_id=self.organization_id)


class TotalTherapistDeserializer(serializers.Serializer):
    period_type = serializers.ChoiceField(
        choices=TotalTherapist.PERIOD_CHOICES
    )
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    is_active = serializers.BooleanField()
    value = serializers.IntegerField()

    class Meta:
        list_serializer_class = TotalTherapistBatchDeserializer

    def validate(self, attrs):
        """
        Ensures the `period_type` carries correct `start_date` and `end_date`.
        """
        period_type = attrs['period_type']
        start_date = attrs['start_date']
        end_date = attrs['end_date']

        if period_type == 'weekly':
            validate_weekly_period(start_date, end_date)

        elif period_type == 'monthly':
            validate_monthly_period(start_date, end_date)

        elif period_type == 'yearly':
            validate_yearly_period(start_date, end_date)

        return attrs


class TotalTherapistInOrgDeserializer(serializers.Serializer):
    period_type = serializers.ChoiceField(
        choices=TotalTherapist.PERIOD_CHOICES
    )
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    is_active = serializers.BooleanField()
    value = serializers.IntegerField()

    class Meta:
        list_serializer_class = TotalTherapistInOrgBatchDeserializer

    def validate(self, attrs):
        """
        Ensures the `period_type` carries correct `start_date` and `end_date`.
        """
        period_type = attrs['period_type']
        start_date = attrs['start_date']
        end_date = attrs['end_date']

        if period_type == 'weekly':
            validate_weekly_period(start_date, end_date)

        elif period_type == 'monthly':
            validate_monthly_period(start_date, end_date)

        elif period_type == 'yearly':
            validate_yearly_period(start_date, end_date)

        return attrs


class TherapistRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TherapistRate
        fields = (
            'organization',
            'period_type',
            'start_date',
            'end_date',
            'type',
            'rate_value',
        )
        read_only = fields


class BaseTherapistRateBatchDeserializer(serializers.ListSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.organization_id = None

    @transaction.atomic
    def create(self, list_rate):
        """
        We override this method to implement upsert the therapists' rates in batch.

        @param list_rate: Validated JSON Array that contains a list of the therapists' rates.
        """
        existing_rates = self.get_existing_rates()

        to_update_objects = self._get_objects_to_update(list_rate, existing_rates)
        to_create_objects = self._get_objects_to_create(list_rate, existing_rates)

        TherapistRate.objects.bulk_update(to_update_objects, fields=['period_type', 'rate_value'])
        rows_created = len(TherapistRate.objects.bulk_create(to_create_objects))
        rows_updated = len(list_rate) - rows_created

        return {'rows_created': rows_created, 'rows_updated': rows_updated}

    def get_existing_rates(self):
        """
        Returns the existing `Rate` objects based on that incoming `list_rate`.
        """
        raise NotImplementedError()

    def _get_objects_to_create(self, list_rate, existing_rates):
        """
        Returns a list of `TherapistRate` objects that are going to be created in batch.

        @param list_rate: Validated JSON Array that contains a list of the therapists' rates.
        @param existing_rates: Existing therapists' rates.
        """
        return [
            TherapistRate(
                organization_id=self.organization_id,
                type=item['type'],
                period_type=item['period_type'],
                start_date=item['start_date'],
                end_date=item['end_date'],
                rate_value=item['rate_value']
            )
            for item in list_rate if self._is_new_item(item, existing_rates)
        ]

    def _is_new_item(self, item, existing_rates):
        """
        Returns `True` if that `item`'s type and period doesn't exist
        in the list of existing therapists' rates.

        @param item: A dictionary that represents the therapist's rate within the payload data.
        @param existing_rates: Existing therapists' rates.
        """
        for rate in existing_rates:
            if bool(
                item['start_date'] == rate.start_date and
                item['end_date'] == rate.end_date and
                item['type'] == rate.type
            ):
                return False

        return True

    def _get_objects_to_update(self, list_rate, existing_rates):
        """
        Returns a list of `TherapistRate` objects that are going to be updated in batch.

        @param list_rate: Validated JSON Array that contains a list of the therapists' rates.
        @param existing_rates: Existing therapists' rates.
        """
        objects_to_update = []

        for item in list_rate:
            pair = self._get_object_to_update(item, existing_rates)

            if pair is None:
                # That `item` doesn't exists,
                # skip it from the update candidates.
                continue

            item, rate = list(pair)
            rate.period_type = item['period_type']
            rate.rate_value = item['rate_value']

            objects_to_update.append(rate)

        return objects_to_update

    def _get_object_to_update(self, item, existing_rates):
        """
        Returns a pair of (`item`, `TherapistRate`)
        if the `item`'s type and period doesn't exist on the existing rates.

        @param item: A dictionary that represents the therapist's rate within the payload data.
        @param existing_rates: Existing therapists' rates.
        """
        for rate in existing_rates:
            if bool(
                item['start_date'] == rate.start_date and
                item['end_date'] == rate.end_date and
                item['type'] == rate.type
            ):
                return (item, rate)

        return None


class TherapistRateBatchDeserializer(BaseTherapistRateBatchDeserializer):

    def get_existing_rates(self):
        """
        Returns the existing `Rate` objects in NiceDay.
        """
        return TherapistRate.objects.filter(organization__isnull=True)


class TherapistRateInOrgBatchDeserializer(BaseTherapistRateBatchDeserializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.organization_id = self.context['organization_id']

    def get_existing_rates(self):
        """
        Returns the existing `Rate` objects in the Organization.
        """
        return TherapistRate.objects.filter(organization_id=self.organization_id)


class TherapistRateDeserializer(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=TherapistRate.TYPE_CHOICES
    )
    period_type = serializers.ChoiceField(
        choices=TherapistRate.PERIOD_CHOICES
    )
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    rate_value = serializers.FloatField()

    class Meta:
        list_serializer_class = TherapistRateBatchDeserializer

    def validate(self, attrs):
        """
        Ensures the `period_type` carries correct `start_date` and `end_date`.
        """
        period_type = attrs['period_type']
        start_date = attrs['start_date']
        end_date = attrs['end_date']

        if period_type == 'weekly':
            validate_weekly_period(start_date, end_date)

        elif period_type == 'monthly':
            validate_monthly_period(start_date, end_date)

        elif period_type == 'yearly':
            validate_yearly_period(start_date, end_date)

        return attrs


class TherapistRateInOrgDeserializer(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=TherapistRate.TYPE_CHOICES
    )
    period_type = serializers.ChoiceField(
        choices=TherapistRate.PERIOD_CHOICES
    )
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    rate_value = serializers.FloatField()

    class Meta:
        list_serializer_class = TherapistRateInOrgBatchDeserializer

    def validate(self, attrs):
        """
        Ensures the `period_type` carries correct `start_date` and `end_date`.
        """
        period_type = attrs['period_type']
        start_date = attrs['start_date']
        end_date = attrs['end_date']

        if period_type == 'weekly':
            validate_weekly_period(start_date, end_date)

        elif period_type == 'monthly':
            validate_monthly_period(start_date, end_date)

        elif period_type == 'yearly':
            validate_yearly_period(start_date, end_date)

        return attrs


class TotalTherapistExportJSONSerializer(serializers.Serializer):

    def to_representation(self, instance):
        return {
            "organization_id": instance.organization_id,
            "type": "active" if instance.is_active else "inactive",
            "period_type": instance.period_type,
            "start_date": instance.start_date.isoformat(),
            "end_date": instance.end_date.isoformat(),
            "value": instance.value
        }


class TotalTherapistExportCSVSerializer(serializers.Serializer):

    def to_representation(self, instance):
        return [
            instance.organization_id,
            "active" if instance.is_active else "inactive",
            instance.period_type,
            instance.start_date.isoformat(),
            instance.end_date.isoformat(),
            instance.value
        ]


class TherapistRateExportJSONSerializer(serializers.Serializer):

    def to_representation(self, instance):
        return {
            "organization_id": instance.organization_id,
            "type": instance.type,
            "period_type": instance.period_type,
            "start_date": instance.start_date.isoformat(),
            "end_date": instance.end_date.isoformat(),
            "rate_value": instance.rate_value
        }


class TherapistRateExportCSVSerializer(serializers.Serializer):

    def to_representation(self, instance):
        return [
            instance.organization_id,
            instance.type,
            instance.period_type,
            instance.start_date.isoformat(),
            instance.end_date.isoformat(),
            instance.rate_value
        ]


class ExportDeserializer(serializers.Serializer):
    TYPE_JSON = 'json'
    TYPE_CSV = 'csv'
    FORMAT_CHOICES = (
        (TYPE_JSON, 'JSON'),
        (TYPE_CSV, 'CSV'),
    )
    format = serializers.ChoiceField(choices=FORMAT_CHOICES)
