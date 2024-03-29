from django.http import Http404
from drf_rw_serializers import generics
from rest_framework import status
from rest_framework.response import Response

from holistic_data_presentation.filters import (
    RateFilter,
    TotalTherapistFilter,
)
from holistic_data_presentation.models import (
    Rate,
    TotalTherapist,
)
from holistic_data_presentation.serializers import (
    BatchCreateSerializer,
    ExportDeserializer,
    RateDeserializer,
    RateExportCSVSerializer,
    RateExportJSONSerializer,
    RatePerOrgDeserializer,
    RateSerializer,
    TotalTherapistDeserializer,
    TotalTherapistExportCSVSerializer,
    TotalTherapistExportJSONSerializer,
    TotalTherapistInOrgDeserializer,
    TotalTherapistSerializer,
)
from holistic_data_presentation.writers import CSVStream


class TotalTherapistListView(generics.ListCreateAPIView):
    read_serializer_class = TotalTherapistSerializer
    write_serializer_class = TotalTherapistDeserializer
    filterset_class = TotalTherapistFilter

    queryset = TotalTherapist.objects.all().order_by('end_date')

    def get_read_serializer_class(self):
        if self.request.method == 'POST':
            return BatchCreateSerializer

        return super().get_read_serializer_class()

    def post(self, request, *args, **kwargs):
        deserializer = self.get_write_serializer(data=request.data, many=True)
        deserializer.is_valid(raise_exception=True)
        deserializer.save()

        serializer = self.get_read_serializer(deserializer.instance)
        return Response(serializer.data)


class TotalTherapistInOrgListView(generics.CreateAPIView):
    read_serializer_class = BatchCreateSerializer
    write_serializer_class = TotalTherapistInOrgDeserializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['organization_id'] = self.kwargs.get('id')
        return context

    def post(self, request, *args, **kwargs):
        if not self.kwargs.get('id'):
            raise Http404

        deserializer = self.get_write_serializer(data=request.data, many=True)
        deserializer.is_valid(raise_exception=True)
        deserializer.save()

        serializer = self.get_read_serializer(deserializer.instance)
        return Response(serializer.data)


class TotalTherapistExportView(generics.CreateAPIView):

    def post(self, request, *args, **kwargs):
        deserializer = ExportDeserializer(data=request.data)
        deserializer.is_valid(raise_exception=True)

        format = deserializer.validated_data['format']
        filename = 'total_therapists'

        queryset = TotalTherapist.objects.all()\
            .order_by('organization', 'is_active', 'period_type', 'start_date')

        if format == 'json':
            serializer = TotalTherapistExportJSONSerializer(
                queryset,
                many=True
            )

            response = Response(serializer.data)
            response['Content-Disposition'] = f"attachment; filename={filename}.json"

            return response

        elif format == 'csv':
            csv_stream = CSVStream()
            headers = [
                'organization_id', 'type', 'period_type',
                'start_date', 'end_date', 'value'
            ]

            return csv_stream.export(
                filename,
                headers,
                queryset.iterator(),
                TotalTherapistExportCSVSerializer
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class RateListView(generics.ListCreateAPIView):
    read_serializer_class = RateSerializer
    write_serializer_class = RateDeserializer
    filterset_class = RateFilter

    queryset = Rate.objects.all().order_by('end_date')

    def get_read_serializer_class(self):
        if self.request.method == 'POST':
            return BatchCreateSerializer

        return super().get_read_serializer_class()

    def post(self, request, *args, **kwargs):
        deserializer = self.get_write_serializer(data=request.data, many=True)
        deserializer.is_valid(raise_exception=True)
        deserializer.save()

        serializer = self.get_read_serializer(deserializer.instance)
        return Response(serializer.data)


class RatePerOrgListView(generics.CreateAPIView):
    read_serializer_class = BatchCreateSerializer
    write_serializer_class = RatePerOrgDeserializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['organization_id'] = self.kwargs.get('id')
        return context

    def post(self, request, *args, **kwargs):
        if not self.kwargs.get('id'):
            raise Http404

        deserializer = self.get_write_serializer(data=request.data, many=True)
        deserializer.is_valid(raise_exception=True)
        deserializer.save()

        serializer = self.get_read_serializer(deserializer.instance)
        return Response(serializer.data)


class RateExportView(generics.CreateAPIView):

    def post(self, request, *args, **kwargs):
        deserializer = ExportDeserializer(data=request.data)
        deserializer.is_valid(raise_exception=True)

        format = deserializer.validated_data['format']
        filename = 'therapists_rates'

        queryset = Rate.objects.all()\
            .order_by('organization', 'type', 'period_type', 'start_date')

        if format == 'json':
            serializer = RateExportJSONSerializer(
                queryset,
                many=True
            )

            response = Response(serializer.data)
            response['Content-Disposition'] = f"attachment; filename={filename}.json"

            return response

        elif format == 'csv':
            csv_stream = CSVStream()
            headers = [
                'organization_id', 'type', 'period_type',
                'start_date', 'end_date', 'value'
            ]

            return csv_stream.export(
                filename,
                headers,
                queryset.iterator(),
                RateExportCSVSerializer
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
