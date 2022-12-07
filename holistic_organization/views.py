import csv

from django.http import Http404, HttpResponse
from drf_rw_serializers import generics
from rest_framework import status
from rest_framework.response import Response

from holistic_organization.models import (
    Organization,
    TherapistInteraction,
)
from holistic_organization.serializers import (
    OrganizationSerializer,
    OrganizationTherapistInteractionJSONSerializer,
    OrganizationTherapistInteractionCSVSerializer,
    OrganizationTherapistInteractionExportDeserializer,
    OrganizationDeserializer,
    SyncSerializer,
    TherapistOrganizationDeserializer,
    TherapistInteractionDeserializer,
)


class OrganizationListView(generics.ListAPIView):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all().order_by('id')


class OrganizationTherapistInteractionListView(generics.CreateAPIView):
    queryset = TherapistInteraction.objects.join_with_organization().order_by('id')

    def post(self, request, *args, **kwargs):

        deserializer = OrganizationTherapistInteractionExportDeserializer(data=request.data)
        deserializer.is_valid(raise_exception=True)

        format = deserializer.validated_data['format']
        filename = 'therapists_interactions'

        if format == 'json':
            return self._get_response_json(filename)

        elif format == 'csv':
            return self._get_response_csv(filename)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def _get_response_json(self, filename: str):

        serializer = OrganizationTherapistInteractionJSONSerializer(self.get_queryset(), many=True)

        return Response(
            data=serializer.data,
            content_type='application/json',
            headers={'Content-Disposition': f'attachment; filename="{filename}.json"'},
        )

    def _get_response_csv(self, filename: str):

        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename="{filename}.csv"'},
        )

        headers = [
            'interaction_id', 'therapist_id', 'chat_count', 'call_count',
            'interaction_date', 'organization_id', 'organization_date_joined'
        ]

        rows = [
            OrganizationTherapistInteractionCSVSerializer().to_representation(instance)
            for instance in self.get_queryset()
        ]

        writer = csv.writer(response)
        writer.writerow(headers)
        writer.writerows(rows)

        return response


class BaseSyncView(generics.CreateAPIView):
    read_serializer_class = SyncSerializer

    def post(self, request, *args, **kwargs):

        deserializer = self.get_write_serializer(data=request.data, many=True)
        deserializer.is_valid(raise_exception=True)
        deserializer.save()

        serializer = self.get_read_serializer(deserializer.instance)
        return Response(serializer.data)


class OrganizationSyncView(BaseSyncView):
    write_serializer_class = OrganizationDeserializer


class TherapistOrganizationSyncView(BaseSyncView):
    write_serializer_class = TherapistOrganizationDeserializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['organization_id'] = self.kwargs.get('id')
        return context

    def post(self, request, *args, **kwargs):
        if not self.kwargs.get('id'):
            raise Http404

        return super().post(request, *args, **kwargs)


class TherapistInteractionSyncView(BaseSyncView):
    write_serializer_class = TherapistInteractionDeserializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['therapist_id'] = self.kwargs.get('id')
        return context

    def post(self, request, *args, **kwargs):
        if not self.kwargs.get('id'):
            raise Http404

        return super().post(request, *args, **kwargs)
