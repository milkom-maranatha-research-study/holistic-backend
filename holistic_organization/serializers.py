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


class TherapistExportJSONSerializer(serializers.Serializer):

    def to_representation(self, instance):
        date_joined = instance.date_joined

        return {
            "therapist_id": instance.id,
            "organization_id": instance.organization_id,
            "organization_date_joined": date_joined.isoformat() if date_joined else None
        }


class TherapistExportCSVSerializer(serializers.Serializer):

    def to_representation(self, instance):
        date_joined = instance.date_joined

        return [
            instance.id,
            instance.organization_id,
            date_joined.isoformat() if date_joined else None
        ]


class InteractionExportJSONSerializer(serializers.Serializer):

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


class InteractionExportCSVSerializer(serializers.Serializer):

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
    def create(self, list_therapists):
        """
        We override this method to implement upsert therapist objects in batch.

        @param list_therapists: Validated JSON Array that contains a list of therapists.
        """
        existing_therapists = Therapist.objects.filter(organization_id=self.organization_id)

        objects_to_update = self._get_objects_to_update(list_therapists, existing_therapists)
        objects_to_create = self._get_objects_to_create(list_therapists, existing_therapists)

        Therapist.objects.bulk_update(objects_to_update, fields=['date_joined'])
        rows_created = len(Therapist.objects.bulk_create(objects_to_create))
        rows_updated = len(list_therapists) - rows_created

        return {'rows_created': rows_created, 'rows_updated': rows_updated}

    def _get_objects_to_create(self, list_therapists, existing_therapists):
        """
        Returns a list of `Therapist` objects that are going to be created
        in batch.

        @param list_therapists: Validated JSON Array that contains a list of therapists.
        @param existing_therapists: Existing therapists.
        """
        return [
            Therapist(
                id=item['therapist_id'],
                organization_id=self.organization_id,
                date_joined=item['date_joined']
            )
            for item in list_therapists if self._is_new_item(item, existing_therapists)
        ]

    def _is_new_item(self, item, existing_therapists):
        """
        Returns `True` if that therapist `item` doesn't exist in the list of existing therapists.

        @param item: A dictionary that represents the Therapist within the payload data.
        @param org_therapists: Existing therapists.
        """
        for therapist in existing_therapists:
            if item['therapist_id'] == therapist.id:
                return False

        return True

    def _get_objects_to_update(self, list_therapists, existing_therapists):
        """
        Returns a list of `Therapist` objects that are going to be updated
        in batch.

        @param list_therapists: Validated JSON Array that contains a list of therapists.
        @param existing_therapists: Existing therapists.
        """
        therapists_to_update = []

        for item in list_therapists:
            pair = self._get_object_to_update(item, existing_therapists)

            if pair is None:
                continue

            item, therapist = list(pair)
            therapist.date_joined = item['date_joined']

            therapists_to_update.append(therapist)

        return therapists_to_update

    def _get_object_to_update(self, item, existing_therapists):
        """
        Returns a pair of (`item`, `Therapist`)
        if that `item` exists on the list of existing therapists.

        @param item: A dictionary that represents the Therapist within the payload data.
        @param existing_therapists: Existing therapists.
        """
        for therapist in existing_therapists:
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
    def create(self, list_interaction):
        """
        We override this method to implement upsert interactions in batch.

        @param list_interaction: Validated JSON Array that contains a list of interactions.
        """
        # 1. Find objects to be created / updated
        existing_interactions = Interaction.objects.filter(therapist_id=self.therapist_id)

        objects_to_update = self._get_objects_to_update(list_interaction, existing_interactions)
        objects_to_create = self._get_objects_to_create(list_interaction, existing_interactions)

        # 2. Special case when creating new interaction objects
        # - We found some interaction objects where the therapist who owned it
        #   doesn't belongs to any Organization.
        # - Hence in that case, we will leave both (`organization` and `date_joined`) fields
        #   to be empty.
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

        # 3. Perform bulk operation to upsert `Interaction` objects
        Interaction.objects.bulk_update(objects_to_update, fields=['chat_count', 'call_count'])
        rows_created = len(Interaction.objects.bulk_create(objects_to_create))
        rows_updated = len(list_interaction) - rows_created

        return {'rows_created': rows_created, 'rows_updated': rows_updated}

    def _get_objects_to_create(self, interaction_list, existing_interactions):
        """
        Returns a list of `Interaction` objects that are going to be created
        in batch.

        @param interaction_list: Validated JSON Array that contains a list of interactions.
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
            for item in interaction_list if self._is_new_item(item, existing_interactions)
        ]

    def _is_new_item(self, item, existing_interactions):
        """
        Returns `True` if that `item` exists in the list of existing interactions.

        @param therapist_id: The therapist identifier.
        @param item: A dictionary that represents the therapist interaction within the payload data.
        @param existing_interactions: Existing interactions.
        """
        for interaction in existing_interactions:
            if bool(
                self.therapist_id == interaction.therapist_id and
                item['interaction_date'] == interaction.interaction_date and
                item['counter'] == interaction.counter
            ):
                return False

        return True

    def _get_objects_to_update(self, list_interaction, existing_interactions):
        """
        Returns a list of `Interaction` objects that are going to be updated
        in batch.

        @param therapist_id: The therapist identifier.
        @param list_interaction: Validated JSON Array that contains a list of interactions.
        @param existing_interactions: Existing interactions.
        """
        interactions_to_update = []

        for item in list_interaction:
            pair = self._get_object_to_update(item, existing_interactions)

            if pair is None:
                continue

            item, interaction = list(pair)
            interaction.chat_count = item['chat_count']
            interaction.call_count = item['call_count']

            interactions_to_update.append(interaction)

        return interactions_to_update

    def _get_object_to_update(self, item, existing_interactions):
        """
        Returns a pair of (`item`, `Interaction`)
        if that `item` exists in the list of existing interactions.

        @param item: A dictionary that represents the therapist interaction within the payload data.
        @param existing_interactions: Existing interactions.
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
