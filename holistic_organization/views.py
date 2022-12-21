from django.http import Http404
from drf_rw_serializers import generics
from rest_framework import status
from rest_framework.response import Response

from holistic_organization.models import (
    Organization,
    TherapistInteraction,
)
from holistic_organization.serializers import (
    OrganizationSerializer,
    JSONExportSerializer,
    CSVExportSerializer,
    ExportDeserializer,
    OrganizationDeserializer,
    SyncSerializer,
    TherapistOrganizationDeserializer,
    TherapistInteractionDeserializer,
)
from holistic_organization.writers import CSVStream


class OrganizationListView(generics.ListAPIView):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all().order_by('id')


class OrganizationTherapistInteractionListView(generics.CreateAPIView):

    def get_queryset(self):
        return TherapistInteraction.objects.annotate_organization_id()\
            .annotate_organization_date_joined().order_by('id')

    def post(self, request, *args, **kwargs):
        deserializer = ExportDeserializer(data=request.data)
        deserializer.is_valid(raise_exception=True)

        format = deserializer.validated_data['format']
        filename = 'therapists_interactions'

        if format == 'json':
            serializer = JSONExportSerializer(self.get_queryset(), many=True)

            response = Response(serializer.data)
            response['Content-Disposition'] = f"attachment; filename={filename}.json"

            return response

        elif format == 'csv':
            headers = [
                'interaction_id', 'therapist_id', 'chat_count', 'call_count',
                'interaction_date', 'organization_id', 'organization_date_joined'
            ]

            csv_stream = CSVStream()

            return csv_stream.export(
                filename, headers, self.get_queryset().iterator(), CSVExportSerializer
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


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
