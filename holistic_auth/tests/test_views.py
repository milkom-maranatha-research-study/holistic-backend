from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.test import APITestCase

from holistic_auth.auth import BasicAuthentication, TokenAuthentication
from holistic_auth.views import (
    UserSerializer,
    UserCreateDeserializer,
    UserUpdateDeserializer
)
from holistic_auth.views import (
    LoginView,
    LogoutView,
    LogoutAllView,
    AccountView,
    AccountDetailView
)


class TestLoginView(APITestCase):
    """
    Test the `LoginView` class
    """

    def setUp(self):
        self.view = LoginView()

    def test_get_authenticator_classes(self):
        actual = [type(authenticator) for authenticator in self.view.get_authenticators()]
        expected = [BasicAuthentication]

        self.assertListEqual(actual, expected)


class TestLogoutView(APITestCase):
    """
    Test the `LogoutView` class
    """

    def setUp(self):
        self.view = LogoutView()

    def test_get_authenticator_classes(self):
        actual = [type(authenticator) for authenticator in self.view.get_authenticators()]
        expected = [TokenAuthentication]

        self.assertListEqual(actual, expected)


class TestLogoutAllView(APITestCase):
    """
    Test the `LogoutAllView` class
    """

    def setUp(self):
        self.view = LogoutAllView()

    def test_get_authenticator_classes(self):
        actual = [type(authenticator) for authenticator in self.view.get_authenticators()]
        expected = [TokenAuthentication]

        self.assertListEqual(actual, expected)


class TestAccountView(APITestCase):
    """
    Test the `AccountView` class
    """

    def setUp(self):
        self.view = AccountView()

    def test_get_read_serializer_class(self):
        self.assertEqual(
            self.view.get_read_serializer_class(),
            UserSerializer
        )

    def test_get_write_serializer_class(self):
        self.assertEqual(
            self.view.get_write_serializer_class(),
            UserCreateDeserializer
        )

    def test_get_permission(self):
        permissions = self.view.get_permissions()

        self.assertEqual(1, len(permissions))
        self.assertIsInstance(permissions[0], AllowAny)


class TestAccountDetailView(APITestCase):
    """
    Test the `AccountDetailView` class
    """

    def setUp(self):
        self.view = AccountDetailView()

    def test_get_read_serializer_class(self):
        self.assertEqual(
            self.view.get_read_serializer_class(),
            UserSerializer
        )

    def test_get_write_serializer_class(self):
        self.assertEqual(
            self.view.get_write_serializer_class(),
            UserUpdateDeserializer
        )

    def test_get_permission(self):
        permissions = self.view.get_permissions()

        self.assertEqual(1, len(permissions))
        self.assertIsInstance(permissions[0], IsAuthenticated)
