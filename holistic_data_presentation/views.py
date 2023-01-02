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
    TherapistRateSerializer,
    TherapistRateDeserializer,
    TotalAllTherapistSerializer,
    TotalAllTherapistDeserializer,
    TotalTherapistSerializer,
    TotalTherapistDeserializer,
)


class TotalAllTherapistListView(generics.CreateAPIView):
    read_serializer_class = TotalAllTherapistSerializer
    write_serializer_class = TotalAllTherapistDeserializer


class TotalTherapistListView(generics.ListAPIView):
    serializer_class = TotalTherapistSerializer
    queryset = TotalTherapist.objects.all().order_by('end_date')
    filterset_class = TotalTherapistFilter


class TotalTherapistDetailView(generics.CreateAPIView):
    read_serializer_class = BatchCreateSerializer
    write_serializer_class = TotalTherapistDeserializer

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


class TherapistRateListView(generics.ListAPIView):
    serializer_class = TherapistRateSerializer
    queryset = TherapistRate.objects.all().order_by('end_date')
    filterset_class = TherapistRateFilter


class TherapistRateDetailView(generics.CreateAPIView):
    read_serializer_class = BatchCreateSerializer
    write_serializer_class = TherapistRateDeserializer

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
