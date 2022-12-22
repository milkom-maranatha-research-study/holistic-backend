from django.db import transaction
from rest_framework import serializers

from holistic_organization.models import (
    Organization,
    Therapist,
    Interaction,
)


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('id', 'name',)
        read_only = fields


class JSONExportSerializer(serializers.Serializer):

    def to_representation(self, instance):
        org_date_joined = instance.organization_date_joined

        return {
            "therapist_id": instance.therapist_id,
            "interaction_date": instance.interaction_date.isoformat(),
            "counter": instance.counter,
            "chat_count": instance.chat_count,
            "call_count": instance.call_count,
            "organization_id": instance.organization_id,
            "organization_date_joined": org_date_joined.isoformat() if org_date_joined else None
        }


class CSVExportSerializer(serializers.Serializer):

    def to_representation(self, instance):
        org_date_joined = instance.organization_date_joined

        return [
            instance.therapist_id,
            instance.interaction_date.isoformat(),
            instance.counter,
            instance.chat_count,
            instance.call_count,
            instance.organization_id,
            org_date_joined.isoformat() if org_date_joined else None
        ]


class ExportDeserializer(serializers.Serializer):
    TYPE_JSON = 'json'
    TYPE_CSV = 'csv'
    FORMAT_CHOICES = (
        (TYPE_JSON, 'JSON'),
        (TYPE_CSV, 'CSV'),
    )
    format = serializers.ChoiceField(choices=FORMAT_CHOICES)


class SyncSerializer(serializers.Serializer):
    rows_created = serializers.IntegerField()
    rows_updated = serializers.IntegerField(required=False)


class OrganizationBatchDeserializer(serializers.ListSerializer):

    @transaction.atomic
    def create(self, organization_list):
        """
        We override this method to implement create organizations in batch.
        Default implementation of the create method will execute create operation one by one.

        @param organization_list: Validated JSON Array that contains a list of organizations.
        """
        org_ids = [item['organization_id'] for item in organization_list]
        existing_org_ids = Organization.objects.all().values_list('id', flat=True)

        org_ids_to_create = list(set(org_ids).difference(existing_org_ids))

        organization_objects = [
            Organization(
                id=org_id,
                name=f"Organization {org_id}"
            )
            for org_id in org_ids_to_create
        ]

        rows_created = len(Organization.objects.bulk_create(organization_objects))
        return {'rows_created': rows_created}


class OrganizationDeserializer(serializers.Serializer):
    organization_id = serializers.IntegerField(
        min_value=1
    )

    class Meta:
        list_serializer_class = OrganizationBatchDeserializer


class TherapistBatchDeserializer(serializers.ListSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.organization_id = self.context['organization_id']

    @transaction.atomic
    def create(self, therapist_list):
        """
        We override this method to implement upsert therapists of the organization in batch.

        @param therapist_list: Validated JSON Array that contains a list of therapists.
        """
        existing_org_therapists = [
            therapist
            for therapist in Therapist.objects.filter(organization_id=self.organization_id)
        ]

        objects_to_update = self._get_therapists_to_update(therapist_list, existing_org_therapists)
        objects_to_create = self._get_therapists_to_create(therapist_list, existing_org_therapists)

        Therapist.objects.bulk_update(objects_to_update, fields=['date_joined'])
        rows_created = len(Therapist.objects.bulk_create(objects_to_create))
        rows_updated = len(therapist_list) - rows_created

        return {'rows_created': rows_created, 'rows_updated': rows_updated}

    def _get_therapists_to_create(self, therapist_list, org_therapists):
        """
        Returns a list of `Therapist` objects that are going to be created
        in batch.

        @param therapist_list: Validated JSON Array that contains a list of therapists.
        @param org_therapists: Existing therapists in the organization.
        """
        return [
            Therapist(
                id=item['therapist_id'],
                organization_id=self.organization_id,
                date_joined=item['date_joined']
            )
            for item in therapist_list if self._is_new_therapist(item, org_therapists)
        ]

    def _is_new_therapist(self, item, org_therapists):
        """
        Returns `True` if that therapist `item` doesn't exist in the list of existing therapists.

        @param item: A dictionary that represents the Therapist within the payload data.
        @param org_therapists: Existing therapists in the organization.
        """
        for therapist in org_therapists:
            if item['therapist_id'] == therapist.id:
                return False

        return True

    def _get_therapists_to_update(self, therapist_list, org_therapists):
        """
        Returns a list of `Therapist` objects that are going to be updated
        in batch.

        @param therapist_list: Validated JSON Array that contains a list of therapists.
        @param org_therapists: Existing therapists in the organization.
        """
        therapists_to_update = []

        for item in therapist_list:
            pair = self._get_pair_of_item(item, org_therapists)

            if pair is None:
                continue

            item, therapist = list(pair)
            therapist.date_joined = item['date_joined']

            therapists_to_update.append(therapist)

        return therapists_to_update

    def _get_pair_of_item(self, item, org_therapists):
        """
        Returns a pair of (`item`, `Therapist`)
        if that therapist `item` exists on the list of existing therapists.

        @param item: A dictionary that represents the Therapist within the payload data.
        @param org_therapists: Existing therapists in the organization.
        """
        for therapist in org_therapists:
            if item['therapist_id'] == therapist.id:
                return (item, therapist)

        return None


class TherapistDeserializer(serializers.Serializer):
    therapist_id = serializers.CharField(
        max_length=32,
        min_length=32
    )
    date_joined = serializers.DateField()

    class Meta:
        list_serializer_class = TherapistBatchDeserializer


class InteractionBatchDeserializer(serializers.ListSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.therapist_id = self.context['therapist_id']

    @transaction.atomic
    def create(self, interaction_list):
        """
        We override this method to implement upesert therapist's interactions in batch.

        @param interaction_list: Validated JSON Array that contains a list of therapist's interactions.
        """
        # 1. Find objects to be created / updated
        existing_interactions = [
            interaction
            for interaction in Interaction.objects.filter(therapist_id=self.therapist_id)
        ]

        objects_to_update = self._get_interactions_to_update(interaction_list, existing_interactions)
        objects_to_create = self._get_interactions_to_create(interaction_list, existing_interactions)

        # 2. Special case when creating new therapists' interaction objects
        # - We found some interaction objects but the therapist who owned it doesn't belongs to any Organization.
        # - Therefore, we perform additional check and add that therapist to the `Therapist` table,
        #   But we leave both (`organization` and `date_joined`) to be empty.
        unknown_ther_ids = []

        if objects_to_create:

            existing_ther_ids = Therapist.objects.filter(
                id__in=[o.therapist_id for o in objects_to_create]
            ).values_list('id', flat=True)

            unknown_ther_ids = set([
                o.therapist_id
                for o in objects_to_create if o.therapist_id not in existing_ther_ids
            ])

        if unknown_ther_ids:
            Therapist.objects.bulk_create(
                [Therapist(id=ther_id)for ther_id in unknown_ther_ids]
            )

        # 3. Perform bulk operation to upsert `TherapistInteraction` objects
        Interaction.objects.bulk_update(objects_to_update, fields=['chat_count', 'call_count'])
        rows_created = len(Interaction.objects.bulk_create(objects_to_create))
        rows_updated = len(interaction_list) - rows_created

        return {'rows_created': rows_created, 'rows_updated': rows_updated}

    def _get_interactions_to_create(self, interaction_list, existing_interactions):
        """
        Returns a list of `Interaction` objects that are going to be created
        in batch.

        @param interaction_list: Validated JSON Array that contains a list of therapist's interactions.
        @param existing_interactions: Existing therapist's interactions.
        """
        return [
            Interaction(
                therapist_id=self.therapist_id,
                interaction_date=item['interaction_date'],
                counter=item['counter'],
                chat_count=item['chat_count'],
                call_count=item['call_count']
            )
            for item in interaction_list if self._is_new_interaction(item, existing_interactions)
        ]

    def _is_new_interaction(self, item, existing_interactions):
        """
        Returns `True` if the combination of unique ids of that interaction `item` exists
        on the list of therapist's interactions.

        @param therapist_id: The therapist identifier.
        @param item: A dictionary that represents the therapist interaction within the payload data.
        @param existing_interactions: Existing therapist's interactions.
        """
        for interaction in existing_interactions:
            if bool(
                self.therapist_id == interaction.therapist_id and
                item['interaction_date'] == interaction.interaction_date and
                item['counter'] == interaction.counter
            ):
                return False

        return True

    def _get_interactions_to_update(self, interaction_list, existing_interactions):
        """
        Returns a list of `Interaction` objects that are going to be updated
        in batch.

        @param therapist_id: The therapist identifier.
        @param interaction_list: Validated JSON Array that contains a list of therapist's interactions.
        @param existing_interactions: Existing therapist's interactions.
        """
        interactions_to_update = []

        for item in interaction_list:
            pair = self._get_pair_of_item(item, existing_interactions)

            if pair is None:
                continue

            item, interaction = list(pair)
            interaction.chat_count = item['chat_count']
            interaction.call_count = item['call_count']

            interactions_to_update.append(interaction)

        return interactions_to_update

    def _get_pair_of_item(self, item, existing_interactions):
        """
        Returns a pair of (`item`, `Interaction`)
        if the combination of unique ids of that interaction `item` exists
        on the list of therapist's interactions.

        @param item: A dictionary that represents the therapist interaction within the payload data.
        @param existing_interactions: Existing therapist's interactions.
        """
        for interaction in existing_interactions:
            if bool(
                self.therapist_id == interaction.therapist_id and
                item['interaction_date'] == interaction.interaction_date and
                item['counter'] == interaction.counter
            ):
                return (item, interaction)

        return None


class InteractionDeserializer(serializers.Serializer):
    counter = serializers.IntegerField(min_value=1)
    interaction_date = serializers.DateField()
    chat_count = serializers.IntegerField(min_value=0)
    call_count = serializers.IntegerField(min_value=0)

    class Meta:
        list_serializer_class = InteractionBatchDeserializer
