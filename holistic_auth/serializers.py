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


class UserDeserializer(serializers.Serializer):
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
