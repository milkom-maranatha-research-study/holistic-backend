from knox import views as knox_views
from drf_rw_serializers import generics
from rest_framework.permissions import AllowAny

from holistic_auth.auth import (
    get_user_model,
    BasicAuthentication,
    TokenAuthentication
)
from holistic_auth.serializers import (
    UserSerializer,
    UserCreateDeserializer,
    UserUpdateDeserializer
)


User = get_user_model()


class LoginView(knox_views.LoginView):
    authentication_classes = [BasicAuthentication]


class LogoutView(knox_views.LogoutView):
    authentication_classes = [TokenAuthentication]


class LogoutAllView(knox_views.LogoutAllView):
    authentication_classes = [TokenAuthentication]


class AccountView(generics.CreateAPIView):
    read_serializer_class = UserSerializer
    write_serializer_class = UserCreateDeserializer
    permission_classes = [AllowAny]


class AccountDetailView(generics.RetrieveUpdateAPIView):
    read_serializer_class = UserSerializer
    write_serializer_class = UserUpdateDeserializer

    def get_object(self):
        return User.objects.get(id=self.request.user.id)
