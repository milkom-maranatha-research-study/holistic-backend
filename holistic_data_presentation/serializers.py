from django.db import transaction
from rest_framework import serializers

from holistic_data_presentation.models import (
    AllTimeNumberOfTherapist,
    AllTimeOrganizationRate,
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


class AllTimeNumberOfTherapistSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllTimeNumberOfTherapist
        fields = (
            'start_date',
            'end_date',
            'is_active',
            'value',
        )
        read_only = fields


class AllTimeNumberOfTherapistDeserializer(serializers.ModelSerializer):
    class Meta:
        model = AllTimeNumberOfTherapist
        fields = (
            'start_date',
            'end_date',
            'is_active',
            'value',
        )

    def get_unique_together_validators(self):
        """
        Returns empty validators.

        The unique together validators are applied on the database level.

        However, we want to disable it on the deserializer level
        because we perform `upsert` instead of `create` operation.
        """
        return []

    def create(self, validated_data):
        """
        Upsert `AllTimeNumberOfTherapist` instance based on these fields
        (`start_date`, `end_date`, `is_active`)
        """
        obj, _ = AllTimeNumberOfTherapist.objects.update_or_create(
            value=validated_data['value'],
            defaults={
                'start_date': validated_data['start_date'],
                'end_date': validated_data['end_date'],
                'is_active': validated_data['is_active']
            },
        )
        return obj


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


class NumberOfTherapistBatchDeserializer(serializers.ListSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.organization_id = self.context['organization_id']

    @transaction.atomic
    def create(self, num_of_therlist):
        """
        We override this method to implement upsert the number of therapists per Organization in batch.

        @param num_of_therlist: Validated JSON Array that contains a list of number of therapists.
        """
        existing_num_of_thers = [
            number_of_ther
            for number_of_ther in NumberOfTherapist.objects.filter(organization_id=self.organization_id)
        ]

        to_update_objects = self._get_objects_to_update(num_of_therlist, existing_num_of_thers)
        to_create_objects = self._get_objects_to_create(num_of_therlist, existing_num_of_thers)

        NumberOfTherapist.objects.bulk_update(to_update_objects, fields=['period_type', 'is_active', 'value'])
        rows_created = len(NumberOfTherapist.objects.bulk_create(to_create_objects))
        rows_updated = len(num_of_therlist) - rows_created

        return {'rows_created': rows_created, 'rows_updated': rows_updated}

    def _get_objects_to_create(self, num_of_ther_list, existing_num_of_thers):
        """
        Returns a list of `NumberOfTherapist` objects that are going to be created in batch.

        @param num_of_ther_list: Validated JSON Array that contains a list of number of therapists.
        @param existing_num_of_thers: Existing number of therapists belonging to the organization.
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
            for item in num_of_ther_list if self._is_new_data(item, existing_num_of_thers)
        ]

    def _is_new_data(self, item, existing_num_of_thers):
        """
        Returns `True` if that `item`'s period doesn't exist
        in the list of existing existing total therapists belonging to the organization.

        @param item: A dictionary that represents the number of therapist within the payload data.
        @param existing_num_of_thers: Existing number of therapists belonging to the organization.
        """
        for num_of_ther in existing_num_of_thers:
            if bool(
                item['is_active'] == num_of_ther.is_active and
                item['start_date'] == num_of_ther.start_date and
                item['end_date'] == num_of_ther.end_date
            ):
                return False

        return True

    def _get_objects_to_update(self, num_of_ther_list, existing_num_of_thers):
        """
        Returns a list of `NumberOfTherapist` objects that are going to be updated in batch.

        @param num_of_ther_list: Validated JSON Array that contains a list of number of therapists.
        @param existing_num_of_thers: Existing number of therapists belonging to the organization.
        """
        objects_to_update = []

        for item in num_of_ther_list:
            pair = self._get_pair_of_item(item, existing_num_of_thers)

            if pair is None:
                # That `item` doesn't exists,
                # skip it from the update candidates.
                continue

            item, num_of_ther = list(pair)
            num_of_ther.period_type = item['period_type']
            num_of_ther.value = item['value']

            objects_to_update.append(num_of_ther)

        return objects_to_update

    def _get_pair_of_item(self, item, existing_num_of_thers):
        """
        Returns a pair of (`item`, `NumberOfTherapist`)
        if the `item`'s period exists on the list of existing total therapists.

        @param item: A dictionary that represents the Therapist within the payload data.
        @param existing_num_of_thers: Existing number of therapists in the organization.
        """
        for num_of_ther in existing_num_of_thers:
            if bool(
                item['is_active'] == num_of_ther.is_active and
                item['start_date'] == num_of_ther.start_date and
                item['end_date'] == num_of_ther.end_date
            ):
                return (item, num_of_ther)

        return None


class NumberOfTherapistDeserializer(serializers.Serializer):
    period_type = serializers.ChoiceField(
        choices=NumberOfTherapist.PERIOD_CHOICES
    )
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    is_active = serializers.BooleanField()
    value = serializers.IntegerField()

    class Meta:
        list_serializer_class = NumberOfTherapistBatchDeserializer

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


class AllTimeOrganizationRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllTimeOrganizationRate
        fields = (
            'start_date',
            'end_date',
            'type',
            'rate_value',
        )
        read_only = fields


class AllTimeOrganizationRateDeserializer(serializers.ModelSerializer):
    class Meta:
        model = AllTimeOrganizationRate
        fields = (
            'start_date',
            'end_date',
            'type',
            'rate_value',
        )

    def get_unique_together_validators(self):
        """
        Returns empty validators.

        The unique together validators are applied on the database level.

        However, we want to disable it on the deserializer level
        because we perform `upsert` instead of `create` operation.
        """
        return []

    def create(self, validated_data):
        """
        Upsert `AllTimeOrganizationRate` instance based on these fields
        (`start_date`, `end_date`, `type`)
        """
        obj, _ = AllTimeOrganizationRate.objects.update_or_create(
            rate_value=validated_data['rate_value'],
            defaults={
                'start_date': validated_data['start_date'],
                'end_date': validated_data['end_date'],
                'type': validated_data['type']
            },
        )
        return obj


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
    def create(self, rate_list):
        """
        We override this method to implement upsert the rates of the Organization in batch.

        @param rate_list: Validated JSON Array that contains a list of the Organization rates.
        """
        existing_rates = [
            rate
            for rate in OrganizationRate.objects.filter(organization_id=self.organization_id)
        ]

        to_update_objects = self._get_objects_to_update(rate_list, existing_rates)
        to_create_objects = self._get_objects_to_create(rate_list, existing_rates)

        OrganizationRate.objects.bulk_update(to_update_objects, fields=['period_type', 'rate_value'])
        rows_created = len(OrganizationRate.objects.bulk_create(to_create_objects))
        rows_updated = len(rate_list) - rows_created

        return {'rows_created': rows_created, 'rows_updated': rows_updated}

    def _get_objects_to_create(self, rate_list, existing_rates):
        """
        Returns a list of `OrganizationRate` objects that are going to be created in batch.

        @param rate_list: Validated JSON Array that contains a list of the organization rates.
        @param existing_rates: Existing rates of the organization.
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
            for item in rate_list if self._is_new_data(item, existing_rates)
        ]

    def _is_new_data(self, item, existing_rates):
        """
        Returns `True` if that `item`'s type and period doesn't exist
        in the list of existing rates of the organization.

        @param item: A dictionary that represents the organization rate within the payload data.
        @param existing_rates: Existing rates of the organization.
        """
        for rate in existing_rates:
            if bool(
                item['type'] == rate.type and
                item['start_date'] == rate.start_date and
                item['end_date'] == rate.end_date
            ):
                return False

        return True

    def _get_objects_to_update(self, rate_list, existing_rates):
        """
        Returns a list of `OrganizationRate` objects that are going to be updated in batch.

        @param rate_list: Validated JSON Array that contains a list of the organization rates.
        @param existing_rates: Existing rates of the organization.
        """
        objects_to_update = []

        for item in rate_list:
            pair = self._get_pair_of_item(item, existing_rates)

            if pair is None:
                # That `item` doesn't exists,
                # skip it from the update candidates.
                continue

            item, rate = list(pair)
            rate.period_type = item['period_type']
            rate.rate_value = item['rate_value']

            objects_to_update.append(rate)

        return objects_to_update

    def _get_pair_of_item(self, item, existing_rates):
        """
        Returns a pair of (`item`, `OrganizationRate`)
        if the `item`'s type and period doesn't exist on the existing rates.

        @param item: A dictionary that represents the organization rate within the payload data.
        @param existing_rates: Existing rates of the organization.
        """
        for rate in existing_rates:
            if bool(
                item['type'] == rate.type and
                item['start_date'] == rate.start_date and
                item['end_date'] == rate.end_date
            ):
                return (item, rate)

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
