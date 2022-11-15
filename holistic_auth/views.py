from knox import views as knox_views
from rest_framework.authentication import BasicAuthentication

from holistic_auth.auth import TokenAuthentication


class LoginView(knox_views.LoginView):
    authentication_classes = [BasicAuthentication]


class LogoutView(knox_views.LogoutView):
    authentication_classes = [TokenAuthentication]


class LogoutAllView(knox_views.LogoutAllView):
    authentication_classes = [TokenAuthentication]
