from knox import views as knox_views
from drf_rw_serializers import generics
from rest_framework.permissions import AllowAny
from rest_framework.authentication import BasicAuthentication

from holistic_auth.auth import TokenAuthentication
from holistic_auth.serializers import (
    UserSerializer,
    UserDeserializer
)


class LoginView(knox_views.LoginView):
    authentication_classes = [BasicAuthentication]


class LogoutView(knox_views.LogoutView):
    authentication_classes = [TokenAuthentication]


class LogoutAllView(knox_views.LogoutAllView):
    authentication_classes = [TokenAuthentication]


class AccountView(generics.CreateAPIView):
    read_serializer_class = UserSerializer
    write_serializer_class = UserDeserializer
    permission_classes = [AllowAny]
