from rest_framework import serializers

from holistic_organization.models import (
    Organization,
    TherapistOrganization,
    TherapistInteraction,
)


class OrganizationBatchDeserializer(serializers.ListSerializer):

    def create(self, validated_data):
        # TODO: Add bulk updsert
        return super().create(validated_data)


class OrganizationDeserializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = (
            'id',
            'name',
        )
        read_only = fields
        list_serializer_class = OrganizationBatchDeserializer


class TherapistOrganizationBatchDeserializer(serializers.ListSerializer):

    def create(self, validated_data):
        # TODO: Add bulk updsert
        return super().create(validated_data)


class TherapistOrganizationDeserializer(serializers.ModelSerializer):

    class Meta:
        model = TherapistOrganization
        fields = (
            'organization',
            'therapist_id',
            'date_joined',
        )
        list_serializer_class = TherapistOrganizationBatchDeserializer


class TherapistInteractionBatchDeserializer(serializers.ListSerializer):

    def create(self, validated_data):
        # TODO: Add bulk updsert
        return super().create(validated_data)


class TherapistInteractionDeserializer(serializers.ModelSerializer):

    class Meta:
        model = TherapistInteraction
        fields = (
            'therapist_id',
            'interaction_date',
            'chat_count',
            'call_count',
        )
        list_serializer_class = TherapistInteractionBatchDeserializer
