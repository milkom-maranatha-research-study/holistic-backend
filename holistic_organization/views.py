from django.http import Http404
from drf_rw_serializers import generics
from rest_framework import status
from rest_framework.response import Response

from holistic_organization.models import (
    Interaction,
    Organization,
    Therapist
)
from holistic_organization.serializers import (
    ExportDeserializer,
    InteractionExportCSVSerializer,
    InteractionExportJSONSerializer,
    InteractionDeserializer,
    OrganizationDeserializer,
    OrganizationSerializer,
    SyncSerializer,
    TherapistDeserializer,
    TherapistExportCSVSerializer,
    TherapistExportJSONSerializer,
)
from holistic_organization.writers import CSVStream


class OrganizationListView(generics.ListAPIView):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all().order_by('id')


class TherapistExportView(generics.CreateAPIView):

    def post(self, request, *args, **kwargs):
        deserializer = ExportDeserializer(data=request.data)
        deserializer.is_valid(raise_exception=True)

        format = deserializer.validated_data['format']
        filename = 'therapists'

        queryset = Therapist.objects.all().order_by('id')

        if format == 'json':
            serializer = TherapistExportJSONSerializer(
                queryset,
                many=True
            )

            response = Response(serializer.data)
            response['Content-Disposition'] = f"attachment; filename={filename}.json"

            return response

        elif format == 'csv':
            csv_stream = CSVStream()
            headers = ['id', 'organization_id', 'date_joined']

            return csv_stream.export(
                filename,
                headers,
                queryset.iterator(),
                TherapistExportCSVSerializer
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class InteractionExportView(generics.CreateAPIView):

    def post(self, request, *args, **kwargs):
        deserializer = ExportDeserializer(data=request.data)
        deserializer.is_valid(raise_exception=True)

        format = deserializer.validated_data['format']
        filename = 'therapists_interactions'

        queryset = Interaction.objects.annotate_organization_id()\
            .annotate_organization_date_joined().order_by('id')

        if format == 'json':
            serializer = InteractionExportJSONSerializer(
                queryset,
                many=True
            )

            response = Response(serializer.data)
            response['Content-Disposition'] = f"attachment; filename={filename}.json"

            return response

        elif format == 'csv':
            csv_stream = CSVStream()
            headers = [
                'therapist_id', 'interaction_date', 'counter',
                'chat_count', 'call_count', 'organization_id',
                'organization_date_joined'
            ]

            return csv_stream.export(
                filename,
                headers,
                queryset.iterator(),
                InteractionExportCSVSerializer
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


class TherapistSyncView(BaseSyncView):
    write_serializer_class = TherapistDeserializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['organization_id'] = self.kwargs.get('id')
        return context

    def post(self, request, *args, **kwargs):
        if not self.kwargs.get('id'):
            raise Http404

        return super().post(request, *args, **kwargs)


class InteractionSyncView(BaseSyncView):
    write_serializer_class = InteractionDeserializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['therapist_id'] = self.kwargs.get('id')
        return context

    def post(self, request, *args, **kwargs):
        if not self.kwargs.get('id'):
            raise Http404

        return super().post(request, *args, **kwargs)
