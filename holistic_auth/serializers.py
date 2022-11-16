from copy import deepcopy
from django.db.models import Q
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'date_joined',
        )
        read_only = fields


class UserCreateDeserializer(serializers.Serializer):
    username = serializers.CharField(max_length=128)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128)
    first_name = serializers.CharField(max_length=32)
    last_name = serializers.CharField(max_length=32)

    def validate(self, data):
        # Validate `username` and `email`
        users = User.objects.filter(
            Q(username__iexact=data['username']) |  # noqa: W504
            Q(email__iexact=data['email'])
        )

        if users.exists():
            raise ValidationError('Username/Email is already exists!')

        return data

    def validate_password(self, value):
        user = User(**self.initial_data)
        user.password = None

        # Execute Django password validation
        validate_password(password=value, user=user)

        return value

    def create(self, validated_data):
        try:
            user = User.objects.create_user(**validated_data, is_active=False)
        except IntegrityError:
            raise ValidationError('Unable to create account.')

        return user


class UserUpdateDeserializer(serializers.ModelSerializer):
    old_password = serializers.CharField(max_length=128, required=False)
    new_password = serializers.CharField(max_length=128, required=False)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'old_password', 'new_password',)

    def validate(self, data):
        # Validate action of updating password
        new_password = data.get('new_password')

        if not new_password:
            return data

        old_password = data.get('old_password')

        # Ensures old password is valid
        if not old_password:
            raise ValidationError('\'old_password\' is required to change your password.')

        if not self.instance.check_password(old_password):
            raise ValidationError('You old password is incorrect.')

        # Ensures the new password is valid
        instance = deepcopy(self.instance)
        instance.first_name = data.get('first_name')
        instance.last_name = data.get('last_name')
        instance.email = data.get('email')

        # Execute Django password validation
        validate_password(password=new_password, user=instance)

        return data

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise ValidationError('Email is already exists!')

        return value

    def update(self, instance, validated_data):
        new_password = validated_data.pop('new_password', None)

        if hasattr(validated_data, 'old_password'):
            del validated_data['old_password']

        instance = super().update(instance, validated_data)

        if new_password:
            instance.set_password(new_password)
            instance.save()

        return instance
