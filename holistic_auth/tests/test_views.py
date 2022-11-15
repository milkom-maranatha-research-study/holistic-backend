from rest_framework.authentication import BasicAuthentication
from rest_framework.test import APITestCase

from holistic_auth.auth import TokenAuthentication
from holistic_auth.views import (
    LoginView,
    LogoutView,
    LogoutAllView
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
