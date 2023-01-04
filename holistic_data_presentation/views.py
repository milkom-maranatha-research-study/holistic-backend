from django.http import Http404
from drf_rw_serializers import generics
from rest_framework.response import Response

from holistic_data_presentation.filters import (
    TherapistRateFilter,
    TotalTherapistFilter,
)
from holistic_data_presentation.models import (
    TherapistRate,
    TotalTherapist,
)
from holistic_data_presentation.serializers import (
    BatchCreateSerializer,
    TherapistRateDeserializer,
    TherapistRateInOrgDeserializer,
    TherapistRateSerializer,
    TotalAllTherapistSerializer,
    TotalAllTherapistDeserializer,
    TotalTherapistDeserializer,
    TotalTherapistInOrgDeserializer,
    TotalTherapistSerializer,
)


class TotalAllTherapistListView(generics.CreateAPIView):
    read_serializer_class = TotalAllTherapistSerializer
    write_serializer_class = TotalAllTherapistDeserializer


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


class TherapistRateListView(generics.ListCreateAPIView):
    read_serializer_class = TherapistRateSerializer
    write_serializer_class = TherapistRateDeserializer
    filterset_class = TherapistRateFilter

    queryset = TherapistRate.objects.all().order_by('end_date')

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


class TherapistRateInOrgListView(generics.CreateAPIView):
    read_serializer_class = BatchCreateSerializer
    write_serializer_class = TherapistRateInOrgDeserializer

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
