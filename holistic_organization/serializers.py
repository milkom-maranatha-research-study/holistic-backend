from django.db import transaction
from rest_framework import serializers

from holistic_organization.models import (
    Organization,
    TherapistOrganization,
    TherapistInteraction,
)


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('id', 'name',)
        read_only = fields


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


class TherapistOrganizationBatchDeserializer(serializers.ListSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.organization_id = self.context['organization_id']

    @transaction.atomic
    def create(self, therapist_list):
        """
        We override this method to implement upsert therapists of the organization in batch.

        @param therapist_list: Validated JSON Array that contains a list of therapists.
        """
        existing_therapists = [
            therapist
            for therapist in TherapistOrganization.objects.filter(organization_id=self.organization_id)
        ]

        to_update_objects = self._get_therapists_to_update(therapist_list, existing_therapists)
        to_create_objects = self._get_therapists_to_create(therapist_list, existing_therapists)

        TherapistOrganization.objects.bulk_update(to_update_objects, fields=['date_joined'])
        rows_created = len(TherapistOrganization.objects.bulk_create(to_create_objects))
        rows_updated = len(therapist_list) - rows_created

        return {'rows_created': rows_created, 'rows_updated': rows_updated}

    def _get_therapists_to_create(self, therapist_list, existing_therapists):
        """
        Returns a list of `TherapistOrganization` objects that are going to be created
        in batch.

        @param therapist_list: Validated JSON Array that contains a list of therapists.
        @param existing_therapists: Existing therapists in the organization.
        """
        return [
            TherapistOrganization(
                organization_id=self.organization_id,
                therapist_id=item['therapist_id'],
                date_joined=item['date_joined']
            )
            for item in therapist_list if self._is_new_therapist(item, existing_therapists)
        ]
    
    def _is_new_therapist(self, item, existing_therapists):
        """
        Returns `True` if that therapist `item` doesn't exist in the list of existing therapists.

        @param item: A dictionary that represents the Therapist within the payload data.
        @param existing_therapists: Existing therapists in the organization.
        """
        for ther_org in existing_therapists:
            if item['therapist_id'] == ther_org.therapist_id:
                return False

        return True

    def _get_therapists_to_update(self, therapist_list, existing_therapists):
        """
        Returns a list of `TherapistOrganization` objects that are going to be updated
        in batch.

        @param therapist_list: Validated JSON Array that contains a list of therapists.
        @param existing_therapists: Existing therapists in the organization.
        """
        therapists_to_update = []

        for item in therapist_list:
            pair = self._get_pair_of_item(item, existing_therapists)

            if pair is None:
                continue

            item, ther_org = list(pair)
            ther_org.date_joined = item['date_joined']

            therapists_to_update.append(ther_org)

        return therapists_to_update

    def _get_pair_of_item(self, item, existing_therapists):
        """
        Returns a pair of (`item`, `TherapistOrganization`)
        if the id of that therapist `item` exists on the list of existing therapists.

        @param item: A dictionary that represents the Therapist within the payload data.
        @param existing_therapists: Existing therapists in the organization.
        """
        for ther_org in existing_therapists:
            if item['therapist_id'] == ther_org.therapist_id:
                return (item, ther_org)

        return None


class TherapistOrganizationDeserializer(serializers.Serializer):
    therapist_id = serializers.CharField(
        max_length=32,
        min_length=32
    )
    date_joined = serializers.DateField()

    class Meta:
        list_serializer_class = TherapistOrganizationBatchDeserializer


class TherapistInteractionBatchDeserializer(serializers.ListSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.therapist_id = self.context['therapist_id']

    @transaction.atomic
    def create(self, interaction_list):
        """
        We override this method to implement upesert therapist's interactions in batch.

        @param interaction_list: Validated JSON Array that contains a list of therapist's interactions.
        """
        existing_interactions = [
            interaction
            for interaction in TherapistInteraction.objects.filter(therapist_id=self.therapist_id)
        ]

        to_update_objects = self._get_interactions_to_update(interaction_list, existing_interactions)
        to_create_objects = self._get_interactions_to_create(interaction_list, existing_interactions)

        TherapistInteraction.objects.bulk_update(to_update_objects, fields=['chat_count', 'call_count'])
        rows_created = len(TherapistInteraction.objects.bulk_create(to_create_objects))
        rows_updated = len(interaction_list) - rows_created

        return {'rows_created': rows_created, 'rows_updated': rows_updated}

    def _get_interactions_to_create(self, interaction_list, existing_interactions):
        """
        Returns a list of `TherapistInteraction` objects that are going to be created
        in batch.

        @param interaction_list: Validated JSON Array that contains a list of therapist's interactions.
        @param existing_interactions: Existing therapist's interactions.
        """
        return [
            TherapistInteraction(
                therapist_id=self.therapist_id,
                interaction_id=item['interaction_id'],
                interaction_date=item['interaction_date'],
                chat_count=item['chat_count'],
                call_count=item['call_count']
            )
            for item in interaction_list if self._is_new_interaction(item, existing_interactions)
        ]
    
    def _is_new_interaction(self, item, existing_interactions):
        """
        Returns `True` if that interaction `item` doesn't exist in the list of therapist's interactions.

        @param therapist_id: The therapist identifier.
        @param item: A dictionary that represents the therapist interaction within the payload data.
        @param existing_interactions: Existing therapist's interactions.
        """
        for interaction in existing_interactions:
            if bool(
                self.therapist_id == interaction.therapist_id and
                item['interaction_id'] == interaction.interaction_id and
                item['interaction_date'] == interaction.interaction_date
            ):
                return False

        return True

    def _get_interactions_to_update(self, interaction_list, existing_interactions):
        """
        Returns a list of `TherapistInteraction` objects that are going to be updated
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
        Returns a pair of (`item`, `TherapistInteraction`)
        if the associated unique ids of that interaction `item` exists
        on the list of therapist's interactions.

        @param item: A dictionary that represents the therapist interaction within the payload data.
        @param existing_interactions: Existing therapist's interactions.
        """
        for interaction in existing_interactions:
            if bool(
                self.therapist_id == interaction.therapist_id and
                item['interaction_id'] == interaction.interaction_id and
                item['interaction_date'] == interaction.interaction_date
            ):
                return (item, interaction)

        return None
        

class TherapistInteractionDeserializer(serializers.Serializer):
    interaction_id = serializers.IntegerField(min_value=1)
    interaction_date = serializers.DateField()
    chat_count = serializers.IntegerField(min_value=0)
    call_count = serializers.IntegerField(min_value=0)

    class Meta:
        list_serializer_class = TherapistInteractionBatchDeserializer
