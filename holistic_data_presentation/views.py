from django.http import Http404
from drf_rw_serializers import generics
from rest_framework.response import Response

from holistic_data_presentation.filters import (
    NumberOfTherapistFilter,
    OrganizationRateFilter
)
from holistic_data_presentation.models import (
    NumberOfTherapist,
    OrganizationRate
)
from holistic_data_presentation.serializers import (
    BatchCreateSerializer,
    NumberOfTherapistSerializer,
    TotalTherapistOrganizationDeserializer,
    OrganizationRateSerializer,
    OrganizationRateDeserializer,
)


class NumberOfTherapistListView(generics.ListAPIView):
    serializer_class = NumberOfTherapistSerializer
    queryset = NumberOfTherapist.objects.all().order_by('id')
    filterset_class = NumberOfTherapistFilter


class NumberOfTherapistDetailView(generics.CreateAPIView):
    read_serializer_class = BatchCreateSerializer
    write_serializer_class = TotalTherapistOrganizationDeserializer

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


class OrganizationRateListView(generics.ListAPIView):
    serializer_class = OrganizationRateSerializer
    queryset = OrganizationRate.objects.all().order_by('id')
    filterset_class = OrganizationRateFilter


class OrganizationRateDetailView(generics.CreateAPIView):
    read_serializer_class = BatchCreateSerializer
    write_serializer_class = OrganizationRateDeserializer

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
