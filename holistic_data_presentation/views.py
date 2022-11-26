from django.http import Http404
from drf_rw_serializers import generics
from rest_framework.response import Response

from holistic_data_presentation.filters import (
    TotalTherapistFilter,
    ChurnRetentionRateFilter
)
from holistic_data_presentation.models import (
    NumberOfTherapist,
    ChurnRetentionRate
)
from holistic_data_presentation.serializers import (
    BatchCreateSerializer,
    TotalTherapistSerializer,
    TotalTherapistOrganizationDeserializer,
    TotalTherapistOrganizationSerializer,
    ChurnRetentionRateSerializer,
    ChurnRetentionRateOrganizationDeserializer,
    ChurnRetentionRateOrganizationSerializer,
)


class BaseTotalTherapistView(generics.GenericAPIView):
    read_serializer_class = TotalTherapistSerializer
    queryset = NumberOfTherapist.objects.all().order_by('id')
    filterset_class = TotalTherapistFilter


class TotalTherapistListView(BaseTotalTherapistView, generics.ListAPIView):
    read_serializer_class = TotalTherapistSerializer


class TotalTherapistPerOrganizationListView(BaseTotalTherapistView, generics.ListCreateAPIView):
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


class BaseChurnRetentionRateView(generics.GenericAPIView):
    read_serializer_class = ChurnRetentionRateSerializer
    queryset = ChurnRetentionRate.objects.all().order_by('id')
    filterset_class = ChurnRetentionRateFilter


class ChurnRetentionRateListView(BaseChurnRetentionRateView, generics.ListAPIView):
    serializer_class = ChurnRetentionRateOrganizationSerializer
    queryset = ChurnRetentionRate.objects.all().order_by('id')


class ChurnRetentionRatePerOrganizationListView(BaseChurnRetentionRateView, generics.ListCreateAPIView):
    read_serializer_class = ChurnRetentionRateOrganizationSerializer
    write_serializer_class = ChurnRetentionRateOrganizationDeserializer

    def get_queryset(self):
        if not self.kwargs.get('id'):
            return ChurnRetentionRate.objects.none()

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
