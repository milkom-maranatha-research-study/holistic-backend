from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError as DjangoValidationError
from model_bakery import baker
from rest_framework.exceptions import ErrorDetail, ValidationError
from rest_framework.test import APIRequestFactory, APITestCase

from holistic_auth.serializers import (
    UserSerializer,
    UserCreateDeserializer,
    UserUpdateDeserializer,
)


User = get_user_model()


class TestUserSerializer(APITestCase):
    """
    Test the `UserSerializer`
    """

    def setUp(self):
        self.factory = APIRequestFactory()
        self.serializer = UserSerializer

    def test_serialization(self):
        user = baker.make(User)

        expected = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'is_active': user.is_active,
            'date_joined': user.date_joined.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        }

        actual = self.serializer(instance=user).data
        self.assertDictEqual(expected, actual)


class TestUserCreateDeserializer(APITestCase):
    """
    Test the `UserCreateDeserializer`
    """

    def setUp(self):
        self.factory = APIRequestFactory()
        self.deserializer = UserCreateDeserializer

    def test_all_params(self):
        """
        Test the deserializer with complete and valid parameters
        """
        data = {
            'username': 'somename',
            'email': 'valid@mail.com',
            'password': 'ValidSecretP4ssw0rd!',
            'first_name': 'Abra',
            'last_name': 'Cadabra'
        }

        deserializer = self.deserializer(data=data)

        try:
            deserializer.is_valid(raise_exception=True)
        except ValidationError:
            self.fail('Boom! You fail the test.')

        instance = deserializer.save()

        self.assertTrue(instance.id is not None)
        self.assertEqual(instance.username, data['username'])
        self.assertEqual(instance.email, data['email'])
        self.assertEqual(instance.first_name, data['first_name'])
        self.assertEqual(instance.last_name, data['last_name'])
        self.assertIsNotNone(instance.date_joined)
        self.assertFalse(instance.is_active)

    def test_missing_all_params(self):
        """
        Test the deserializer with missing all params
        """
        data = {}

        deserializer = self.deserializer(data=data)

        with self.assertRaises(ValidationError) as error:
            deserializer.is_valid(raise_exception=True)

        self.assertEqual(
            error.exception.detail,
            {
                'username': [ErrorDetail(string='This field is required.', code='required')],
                'password': [ErrorDetail(string='This field is required.', code='required')],
                'email': [ErrorDetail(string='This field is required.', code='required')],
                'first_name': [ErrorDetail(string='This field is required.', code='required')],
                'last_name': [ErrorDetail(string='This field is required.', code='required')],
            }
        )

    def test_blank_params(self):
        """
        Test the deserializer with blank params
        """
        data = {
            'username': '',
            'email': '',
            'password': '',
            'first_name': '',
            'last_name': '',
        }

        deserializer = self.deserializer(data=data)

        with self.assertRaises(ValidationError) as error:
            deserializer.is_valid(raise_exception=True)

        self.assertDictEqual(
            error.exception.detail,
            {
                'username': [ErrorDetail(string='This field may not be blank.', code='blank')],
                'password': [ErrorDetail(string='This field may not be blank.', code='blank')],
                'email': [ErrorDetail(string='This field may not be blank.', code='blank')],
                'first_name': [ErrorDetail(string='This field may not be blank.', code='blank')],
                'last_name': [ErrorDetail(string='This field may not be blank.', code='blank')],
            }
        )

    def test_invalid_email_param(self):
        """
        Test the deserializer with invalid email param
        """
        data = {
            'username': 'somename',
            'email': 'invalidmail.com',
            'password': 'ValidSecretP4ssw0rd!',
            'first_name': 'Abra',
            'last_name': 'Cadabra',
        }

        deserializer = self.deserializer(data=data)

        with self.assertRaises(ValidationError) as error:
            deserializer.is_valid(raise_exception=True)

        self.assertDictEqual(
            error.exception.detail,
            {
                'email': [ErrorDetail(string='Enter a valid email address.', code='invalid')]
            }
        )

    def test_validate_1(self):
        """
        Test the deserializer `.validate` method with username that is already used (case insensitive).
        """
        email = 'test@test.com'
        baker.make(User, email=email)

        data = {
            'username': 'somename',
            'email': email.capitalize(),
            'password': 'ValidSecretP4ssw0rd!',
            'first_name': 'Abra',
            'last_name': 'Cadabra',
        }

        deserializer = self.deserializer(data=data)

        with self.assertRaises(ValidationError) as error:
            deserializer.validate(data)

        self.assertEqual(
            error.exception.detail,
            [
                ErrorDetail(string='Username/Email is already exists!', code='invalid')
            ]
        )

    def test_validate_2(self):
        """
        Test the deserializer `.validate` method with email address that is already used (case insensitive).
        """
        username = 'somename'
        baker.make(User, username=username)

        data = {
            'username': username.capitalize(),
            'email': 'test@mail.com',
            'password': 'ValidSecretP4ssw0rd!',
            'first_name': 'Abra',
            'last_name': 'Cadabra',
        }

        deserializer = self.deserializer(data=data)

        with self.assertRaises(ValidationError) as error:
            deserializer.validate(data)

        self.assertEqual(
            error.exception.detail,
            [
                ErrorDetail(string='Username/Email is already exists!', code='invalid')
            ]
        )

    def test_validate_password_1(self):
        """
        Test the deserializer `.validate_password` method with invalid password
        """
        data = {
            'username': 'somename',
            'email': 'somename@mail.com',
            'password': '0123456',
            'first_name': 'Abra',
            'last_name': 'Cadabra',
        }

        deserializer = self.deserializer(data=data)

        with self.assertRaises(DjangoValidationError) as error:
            deserializer.validate_password(data['password'])

        self.assertCountEqual(
            error.exception.messages,
            [
                'This password is too short. It must contain at least 8 characters.',
                'This password is too common.',
                'This password is entirely numeric.'
            ]
        )

    def test_validate_password_2(self):
        """
        Test the deserializer `.validate_password` method with password's value that is too similar with `username`.
        """
        data = {
            'username': 'somename',
            'email': 'Valid123@mail.com',
            'password': 'somename',
            'first_name': 'Abra',
            'last_name': 'Cadabra',
        }

        deserializer = self.deserializer(data=data)

        with self.assertRaises(DjangoValidationError) as error:
            deserializer.validate_password(data['password'])

        self.assertListEqual(
            error.exception.messages,
            ['The password is too similar to the username.']
        )

    def test_validate_password_3(self):
        """
        Test the deserializer `.validate_password` method with password's value that is too similar with `email`.
        """
        data = {
            'username': 'somename',
            'email': 'Valid123@mail.com',
            'password': 'Valid123@mail.com',
            'first_name': 'Abra',
            'last_name': 'Cadabra',
        }

        deserializer = self.deserializer(data=data)

        with self.assertRaises(DjangoValidationError) as error:
            deserializer.validate_password(data['password'])

        self.assertListEqual(
            error.exception.messages,
            ['The password is too similar to the email address.']
        )

    def test_validate_password_4(self):
        """
        Test the deserializer `.validate_password` method with password's value that is too similar with `first_name`.
        """
        data = {
            'username': 'somename',
            'email': 'Valid123@mail.com',
            'password': 'Abra123456!',
            'first_name': 'Abra123456!',
            'last_name': 'Cadabra',
        }

        deserializer = self.deserializer(data=data)

        with self.assertRaises(DjangoValidationError) as error:
            deserializer.validate_password(data['password'])

        self.assertListEqual(
            error.exception.messages,
            ['The password is too similar to the first name.']
        )

    def test_validate_password_5(self):
        """
        Test the deserializer `.validate_password` method with password's value that is too similar with `last_name`.
        """
        data = {
            'username': 'somename',
            'email': 'Valid123@mail.com',
            'password': 'cAdabra123456!',
            'first_name': 'Abra',
            'last_name': 'Cadabra123456!',
        }

        deserializer = self.deserializer(data=data)

        with self.assertRaises(DjangoValidationError) as error:
            deserializer.validate_password(data['password'])

        self.assertListEqual(
            error.exception.messages,
            ['The password is too similar to the last name.']
        )


class TestUserUpdateDeserializer(APITestCase):
    """
    Test the `UserUpdateDeserializer`
    """

    def setUp(self):
        self.factory = APIRequestFactory()
        self.deserializer = UserUpdateDeserializer

    def test_all_params(self):
        """
        Test the deserializer with complete and valid parameters
        """
        old_password = 'ValidSecretP4ssw0rd!'

        instance = baker.make(User)
        instance.password = make_password(old_password)
        instance.save()

        data = {
            'email': 'valid@mail.com',
            'old_password': old_password,
            'new_password': 'SuperSecretP4ssw0rd',
            'first_name': 'Abra',
            'last_name': 'Cadabra'
        }

        deserializer = self.deserializer(instance=instance, data=data)

        try:
            deserializer.is_valid(raise_exception=True)
        except ValidationError:
            self.fail('Boom! You fail the test.')

        instance = deserializer.save()

        self.assertEqual(instance.email, data['email'])
        self.assertEqual(instance.first_name, data['first_name'])
        self.assertEqual(instance.last_name, data['last_name'])

    def test_missing_all_params(self):
        """
        Test the deserializer with missing all params
        """
        instance = baker.make(User)

        data = {}

        deserializer = self.deserializer(instance=instance, data=data)

        try:
            deserializer.is_valid(raise_exception=True)
        except ValidationError:
            self.fail('Boom! You fail the test.')

    def test_blank_params(self):
        """
        Test the deserializer with blank params
        """
        instance = baker.make(User, _fill_optional=True)

        data = {
            'username': '',
            'email': '',
            'first_name': '',
            'last_name': '',
        }

        deserializer = self.deserializer(instance=instance, data=data)

        try:
            deserializer.is_valid(raise_exception=True)
        except ValidationError:
            self.fail('Boom! You fail the test.')

    def test_invalid_email_param(self):
        """
        Test the deserializer with invalid email param
        """
        instance = baker.make(User)

        data = {
            'username': 'somename',
            'email': 'invalidmail.com',
            'first_name': 'Abra',
            'last_name': 'Cadabra',
        }

        deserializer = self.deserializer(instance=instance, data=data)

        with self.assertRaises(ValidationError) as error:
            deserializer.is_valid(raise_exception=True)

        self.assertDictEqual(
            error.exception.detail,
            {
                'email': [ErrorDetail(string='Enter a valid email address.', code='invalid')]
            }
        )

    def test_validate_1(self):
        """
        Test the deserializer `.validate` method with invalid password
        """
        old_password = 'old_password'

        instance = baker.make(User)
        instance.password = make_password(old_password)
        instance.save()

        data = {
            'username': 'somename',
            'email': 'somename@mail.com',
            'old_password': old_password,
            'new_password': '0123456',
            'first_name': 'Abra',
            'last_name': 'Cadabra',
        }

        deserializer = self.deserializer(instance=instance, data=data)

        with self.assertRaises(DjangoValidationError) as error:
            deserializer.validate(data)

        self.assertCountEqual(
            error.exception.messages,
            [
                'This password is too short. It must contain at least 8 characters.',
                'This password is too common.',
                'This password is entirely numeric.'
            ]
        )

    def test_validate_2(self):
        """
        Test the deserializer `.validate_password` method with password's value that is too similar with `username`.
        """
        old_password = 'old_password'

        instance = baker.make(User)
        instance.password = make_password(old_password)
        instance.save()

        data = {
            'email': 'Valid123@mail.com',
            'old_password': old_password,
            'new_password': instance.username,
            'first_name': 'Abra',
            'last_name': 'Cadabra',
        }

        deserializer = self.deserializer(instance=instance, data=data)

        with self.assertRaises(DjangoValidationError) as error:
            deserializer.validate(data)

        self.assertListEqual(
            error.exception.messages,
            ['The password is too similar to the username.']
        )

    def test_validate_3(self):
        """
        Test the deserializer `.validate_password` method with password's value that is too similar with `email`.
        """
        old_password = 'old_password'

        instance = baker.make(User)
        instance.password = make_password(old_password)
        instance.save()

        data = {
            'username': 'somename',
            'email': 'Valid123@mail.com',
            'old_password': old_password,
            'new_password': 'Valid123@mail.com',
            'first_name': 'Abra',
            'last_name': 'Cadabra',
        }

        deserializer = self.deserializer(instance=instance, data=data)

        with self.assertRaises(DjangoValidationError) as error:
            deserializer.validate(data)

        self.assertListEqual(
            error.exception.messages,
            ['The password is too similar to the email address.']
        )

    def test_validate_4(self):
        """
        Test the deserializer `.validate_password` method with password's value that is too similar with `first_name`.
        """
        old_password = 'old_password'

        instance = baker.make(User)
        instance.password = make_password(old_password)
        instance.save()

        data = {
            'username': 'somename',
            'email': 'Valid123@mail.com',
            'old_password': old_password,
            'new_password': 'Abra123456!',
            'first_name': 'Abra123456!',
            'last_name': 'Cadabra',
        }

        deserializer = self.deserializer(instance=instance, data=data)

        with self.assertRaises(DjangoValidationError) as error:
            deserializer.validate(data)

        self.assertListEqual(
            error.exception.messages,
            ['The password is too similar to the first name.']
        )

    def test_validate_5(self):
        """
        Test the deserializer `.validate_password` method with password's value that is too similar with `last_name`.
        """
        old_password = 'old_password'

        instance = baker.make(User)
        instance.password = make_password(old_password)
        instance.save()

        data = {
            'username': 'somename',
            'email': 'Valid123@mail.com',
            'old_password': old_password,
            'new_password': 'cAdabra123456!',
            'first_name': 'Abra',
            'last_name': 'Cadabra123456!',
        }

        deserializer = self.deserializer(instance=instance, data=data)

        with self.assertRaises(DjangoValidationError) as error:
            deserializer.validate(data)

        self.assertListEqual(
            error.exception.messages,
            ['The password is too similar to the last name.']
        )

    def test_validate_email(self):
        """
        Test the deserializer `.validate_email` method with email that is already used (case insensitive).
        """
        email = 'test@test.com'
        instance = baker.make(User, email=email)

        data = {
            'username': 'somename',
            'email': email.capitalize(),
            'password': 'ValidSecretP4ssw0rd!',
            'first_name': 'Abra',
            'last_name': 'Cadabra',
        }

        deserializer = self.deserializer(instance, data=data)

        with self.assertRaises(ValidationError) as error:
            deserializer.validate_email(email.capitalize())

        self.assertEqual(
            error.exception.detail,
            [
                ErrorDetail(string='Email is already exists!', code='invalid')
            ]
        )
