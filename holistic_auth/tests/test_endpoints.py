from unittest import mock
from model_bakery import baker
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase


User = get_user_model()


class TestLoginEndpoint(APITestCase):
    """
    Test endpoint `/auth/login/`
    """

    def setUp(self):
        self.user = baker.make(User)
        self.client.force_authenticate(self.user)

        self.url = '/auth/login/'

    def test_post(self):
        response = self.client.post(self.url)
        self.assertNotEqual(response.status_code,
                            status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put(self):
        response = self.client.put(self.url)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)


class TestLogoutEndpoint(APITestCase):
    """
    Test endpoint `/auth/logout/`
    """

    def setUp(self):
        self.user = baker.make(User)
        self.client.force_authenticate(self.user)

        self.url = '/auth/logout/'

    @mock.patch('holistic_auth.views.LogoutView.post')
    def test_post(self, mock_post):
        # We need to mock the HTTP POST method
        # because we don't have an access to the view's `request._auth` object.
        mock_post.return_value = Response(None, status=status.HTTP_204_NO_CONTENT)

        response = self.client.post(self.url)
        self.assertNotEqual(response.status_code,
                            status.HTTP_405_METHOD_NOT_ALLOWED)

        mock_post.assert_called_once()

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put(self):
        response = self.client.put(self.url)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)


class TestLogoutAllEndpoint(APITestCase):
    """
    Test endpoint `/auth/logout-all/`
    """

    def setUp(self):
        self.user = baker.make(User)
        self.client.force_authenticate(self.user)

        self.url = '/auth/logout-all/'

    def test_post(self):
        response = self.client.post(self.url)
        self.assertNotEqual(response.status_code,
                            status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put(self):
        response = self.client.put(self.url)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)


class TestAccountEndpoint(APITestCase):
    """
    Test endpoint `/accounts/`
    """

    def setUp(self):
        self.user = baker.make(User)
        self.client.force_authenticate(self.user)

        self.url = '/accounts/'

    def test_post(self):
        response = self.client.post(self.url)
        self.assertNotEqual(response.status_code,
                            status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put(self):
        response = self.client.put(self.url)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)


class TestAccountMeEndpoint(APITestCase):
    """
    Test endpoint `/accounts/me/`
    """

    def setUp(self):
        self.user = baker.make(User)
        self.client.force_authenticate(self.user)

        self.url = '/accounts/me/'

    def test_post(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code,
                            status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put(self):
        response = self.client.put(self.url)
        self.assertNotEqual(response.status_code,
                            status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
