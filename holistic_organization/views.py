from django.http import Http404
from drf_rw_serializers import generics
from rest_framework.response import Response

from holistic_organization.models import Organization
from holistic_organization.serializers import (
    OrganizationSerializer,
    OrganizationDeserializer,
    SyncSerializer,
    TherapistOrganizationDeserializer,
    TherapistInteractionDeserializer
)


class OrganizationListView(generics.ListAPIView):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all().order_by('id')


class BaseSyncView(generics.CreateAPIView):
    read_serializer_class = SyncSerializer

    def post(self, request, *args, **kwargs):

        deserializer = self.get_write_serializer(data=request.data, many=True)
        deserializer.is_valid(raise_exception=True)
        deserializer.save()

        print(deserializer.instance)
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
