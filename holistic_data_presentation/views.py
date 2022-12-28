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
    TotalTherapistOrganizationSerializer,
    OrganizationRateSerializer,
    OrganizationRateDeserializer,
)


class BaseTotalTherapistView(generics.GenericAPIView):
    read_serializer_class = NumberOfTherapistSerializer
    queryset = NumberOfTherapist.objects.all().order_by('id')
    filterset_class = NumberOfTherapistFilter


class NumberOfTherapistListView(BaseTotalTherapistView, generics.ListAPIView):
    read_serializer_class = NumberOfTherapistSerializer


class NumberOfTherapistDetailView(BaseTotalTherapistView, generics.ListCreateAPIView):
    read_serializer_class = TotalTherapistOrganizationSerializer
    write_serializer_class = TotalTherapistOrganizationDeserializer

    def get_queryset(self):
        if not self.kwargs.get('id'):
            return NumberOfTherapist.objects.none()

        return super().get_queryset().filter(organization_id=self.kwargs.get('id'))

    def get_serializer_context(self):
        context = super().get_serializer_context()

        if self.request.method == 'POST':
            context['organization_id'] = self.kwargs.get('id')

        return context

    def get_read_serializer_class(self):
        if self.request.method == 'POST':
            return BatchCreateSerializer

        return super().get_read_serializer_class()

    def post(self, request, *args, **kwargs):
        if not self.kwargs.get('id'):
            raise Http404

        deserializer = self.get_write_serializer(data=request.data, many=True)
        deserializer.is_valid(raise_exception=True)
        deserializer.save()

        serializer = self.get_read_serializer(deserializer.instance)
        return Response(serializer.data)


class BaseOrganizationRateView(generics.GenericAPIView):
    read_serializer_class = OrganizationRateSerializer
    queryset = OrganizationRate.objects.all().order_by('id')
    filterset_class = OrganizationRateFilter


class OrganizationRateListView(BaseOrganizationRateView, generics.ListAPIView):
    queryset = OrganizationRate.objects.all().order_by('id')


class OrganizationRateDetailView(BaseOrganizationRateView, generics.ListCreateAPIView):
    write_serializer_class = OrganizationRateDeserializer

    def get_queryset(self):
        if not self.kwargs.get('id'):
            return OrganizationRate.objects.none()

        return super().get_queryset().filter(organization_id=self.kwargs.get('id'))

    def get_serializer_context(self):
        context = super().get_serializer_context()

        if self.request.method == 'POST':
            context['organization_id'] = self.kwargs.get('id')

        return context

    def get_read_serializer_class(self):
        if self.request.method == 'POST':
            return BatchCreateSerializer

        return super().get_read_serializer_class()

    def post(self, request, *args, **kwargs):
        if not self.kwargs.get('id'):
            raise Http404

        deserializer = self.get_write_serializer(data=request.data, many=True)
        deserializer.is_valid(raise_exception=True)
        deserializer.save()

        serializer = self.get_read_serializer(deserializer.instance)
        return Response(serializer.data)
