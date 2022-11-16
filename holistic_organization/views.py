from drf_rw_serializers import generics
from rest_framework import status
from rest_framework.response import Response

from holistic_organization.serializers import (
    OrganizationDeserializer,
    TherapistOrganizationDeserializer,
    TherapistInteractionDeserializer
)


class BaseSyncView(generics.CreateAPIView):

    def put(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_200_OK)


class OrganizationSyncView(BaseSyncView):
    serializer_class = OrganizationDeserializer


class TherapistOrganizationSyncView(BaseSyncView):
    serializer_class = TherapistOrganizationDeserializer


class TherapistInteractionSyncView(BaseSyncView):
    serializer_class = TherapistInteractionDeserializer
