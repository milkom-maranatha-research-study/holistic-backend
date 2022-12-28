from django.db import transaction
from rest_framework import serializers

from holistic_data_presentation.models import (
    NumberOfTherapist,
    OrganizationRate,
)
from holistic_data_presentation.validators import (
    validate_weekly_period,
    validate_monthly_period,
    validate_yearly_period,
)


class BatchCreateSerializer(serializers.Serializer):
    rows_created = serializers.IntegerField()
    rows_updated = serializers.IntegerField(required=False)


class NumberOfTherapistSerializer(serializers.ModelSerializer):
    class Meta:
        model = NumberOfTherapist
        fields = (
            'period_type',
            'organization',
            'start_date',
            'end_date',
            'is_active',
            'value',
        )
        read_only = fields


class TotalTherapistOrganizationBatchDeserializer(serializers.ListSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.organization_id = self.context['organization_id']

    @transaction.atomic
    def create(self, total_therapist_list):
        """
        We override this method to implement upsert the number of therapists per Organization in batch.

        @param total_therapist_list: Validated JSON Array that contains a list of number of therapists.
        """
        existing_total_therapists = [
            number_of_ther
            for number_of_ther in NumberOfTherapist.objects.filter(organization_id=self.organization_id)
        ]

        to_update_objects = self._get_objects_to_update(total_therapist_list, existing_total_therapists)
        to_create_objects = self._get_objects_to_create(total_therapist_list, existing_total_therapists)

        NumberOfTherapist.objects.bulk_update(to_update_objects, fields=['period_type', 'is_active', 'value'])
        rows_created = len(NumberOfTherapist.objects.bulk_create(to_create_objects))
        rows_updated = len(total_therapist_list) - rows_created

        return {'rows_created': rows_created, 'rows_updated': rows_updated}

    def _get_objects_to_create(self, total_therapist_list, existing_total_therapists):
        """
        Returns a list of `NumberOfTherapist` objects that are going to be created in batch.

        @param total_therapist_list: Validated JSON Array that contains a list of number of therapists.
        @param existing_total_therapists: Existing number of therapists belonging to the organization.
        """
        return [
            NumberOfTherapist(
                organization_id=self.organization_id,
                period_type=item['period_type'],
                start_date=item['start_date'],
                end_date=item['end_date'],
                is_active=item['is_active'],
                value=item['value']
            )
            for item in total_therapist_list if self._is_new_data(item, existing_total_therapists)
        ]

    def _is_new_data(self, item, existing_total_therapists):
        """
        Returns `True` if that `item`'s period doesn't exist
        in the list of existing existing total therapists belonging to the organization.

        @param item: A dictionary that represents the number of therapist within the payload data.
        @param existing_total_therapists: Existing number of therapists belonging to the organization.
        """
        for total_therapist in existing_total_therapists:
            if bool(
                item['start_date'] == total_therapist.start_date and
                item['end_date'] == total_therapist.end_date
            ):
                return False

        return True

    def _get_objects_to_update(self, total_therapist_list, existing_total_therapists):
        """
        Returns a list of `NumberOfTherapist` objects that are going to be updated in batch.

        @param total_therapist_list: Validated JSON Array that contains a list of number of therapists.
        @param existing_total_therapists: Existing number of therapists belonging to the organization.
        """
        objects_to_update = []

        for item in total_therapist_list:
            pair = self._get_pair_of_item(item, existing_total_therapists)

            if pair is None:
                continue

            item, total_therapist = list(pair)
            total_therapist.period_type = item['period_type']
            total_therapist.value = item['value']

            objects_to_update.append(total_therapist)

        return objects_to_update

    def _get_pair_of_item(self, item, existing_total_therapists):
        """
        Returns a pair of (`item`, `NumberOfTherapist`)
        if the `item`'s period exists on the list of existing total therapists.

        @param item: A dictionary that represents the Therapist within the payload data.
        @param existing_therapists: Existing therapists in the organization.
        """
        for total_therapist in existing_total_therapists:
            if bool(
                item['start_date'] == total_therapist.start_date and
                item['end_date'] == total_therapist.end_date
            ):
                return (item, total_therapist)

        return None


class TotalTherapistOrganizationDeserializer(serializers.Serializer):
    period_type = serializers.ChoiceField(
        choices=NumberOfTherapist.PERIOD_CHOICES
    )
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    is_active = serializers.BooleanField()
    value = serializers.IntegerField()

    class Meta:
        list_serializer_class = TotalTherapistOrganizationBatchDeserializer

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


class OrganizationRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationRate
        fields = (
            'organization',
            'period_type',
            'start_date',
            'end_date',
            'type',
            'rate_value',
        )
        read_only = fields


class OrganizationRateBatchDeserializer(serializers.ListSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.organization_id = self.context['organization_id']

    @transaction.atomic
    def create(self, churn_retention_rate_list):
        """
        We override this method to implement upsert the churn/retention rates per Organization in batch.

        @param churn_retention_rate_list: Validated JSON Array that contains a list of the churn/retention rates.
        """
        existing_churn_retention_rates = [
            number_of_ther
            for number_of_ther in OrganizationRate.objects.filter(organization_id=self.organization_id)
        ]

        to_update_objects = self._get_objects_to_update(churn_retention_rate_list, existing_churn_retention_rates)
        to_create_objects = self._get_objects_to_create(churn_retention_rate_list, existing_churn_retention_rates)

        OrganizationRate.objects.bulk_update(to_update_objects, fields=['period_type', 'rate_value'])
        rows_created = len(OrganizationRate.objects.bulk_create(to_create_objects))
        rows_updated = len(churn_retention_rate_list) - rows_created

        return {'rows_created': rows_created, 'rows_updated': rows_updated}

    def _get_objects_to_create(self, churn_retention_rate_list, existing_churn_retention_rates):
        """
        Returns a list of `ChurnRetentionRate` objects that are going to be created in batch.

        @param churn_retention_rate_list: Validated JSON Array that contains a list of the churn/retention rates.
        @param existing_churn_retention_rates: Existing churn/retention rates of the organization.
        """
        return [
            OrganizationRate(
                organization_id=self.organization_id,
                type=item['type'],
                period_type=item['period_type'],
                start_date=item['start_date'],
                end_date=item['end_date'],
                rate_value=item['rate_value']
            )
            for item in churn_retention_rate_list if self._is_new_data(item, existing_churn_retention_rates)
        ]

    def _is_new_data(self, item, existing_churn_retention_rates):
        """
        Returns `True` if that `item`'s type and period doesn't exist
        in the list of existing churn/retention rate of the organization.

        @param item: A dictionary that represents the churn/retention rate within the payload data.
        @param existing_churn_retention_rates: Existing churn/retention rates of the organization.
        """
        for churn_retention_rate in existing_churn_retention_rates:
            if bool(
                item['type'] == churn_retention_rate.type and
                item['start_date'] == churn_retention_rate.start_date and
                item['end_date'] == churn_retention_rate.end_date
            ):
                return False

        return True

    def _get_objects_to_update(self, churn_retention_rate_list, existing_churn_retention_rates):
        """
        Returns a list of `ChurnRetentionRate` objects that are going to be updated in batch.

        @param churn_retention_rate_list: Validated JSON Array that contains a list of the churn/retention rates.
        @param existing_churn_retention_rates: Existing churn/retention rates of the organization.
        """
        objects_to_update = []

        for item in churn_retention_rate_list:
            pair = self._get_pair_of_item(item, existing_churn_retention_rates)

            if pair is None:
                continue

            item, churn_retention_rate = list(pair)
            churn_retention_rate.period_type = item['period_type']
            churn_retention_rate.rate_value = item['rate_value']

            objects_to_update.append(churn_retention_rate)

        return objects_to_update

    def _get_pair_of_item(self, item, existing_churn_retention_rates):
        """
        Returns a pair of (`item`, `ChurnRetentionRate`)
        if the `item`'s type and period doesn't exist on the list of existing total therapists.

        @param item: A dictionary that represents the churn/retention rate within the payload data.
        @param existing_churn_retention_rates: Existing churn/retention rates of the organization.
        """
        for churn_retention_rate in existing_churn_retention_rates:
            if bool(
                item['type'] == churn_retention_rate.type and
                item['start_date'] == churn_retention_rate.start_date and
                item['end_date'] == churn_retention_rate.end_date
            ):
                return (item, churn_retention_rate)

        return None


class OrganizationRateDeserializer(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=OrganizationRate.TYPE_CHOICES
    )
    period_type = serializers.ChoiceField(
        choices=OrganizationRate.PERIOD_CHOICES
    )
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    rate_value = serializers.FloatField()

    class Meta:
        list_serializer_class = OrganizationRateBatchDeserializer

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
