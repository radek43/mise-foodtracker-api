"""Serializers for the user API view"""
from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = get_user_model()

        # fields that are allowed by the user to change
        fields = ['email', 'password', 'name']

        # extra metadata to password field
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    # the method will be called if the validation is successful
    def create(self, validated_data):
        """Create and return a user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user"""

        # remove password from result
        password = validated_data.pop('password', None)

        # update object
        user = super().update(instance, validated_data)

        # update password the user changes it
        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_style': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate user"""

        # get user and password from user
        email = attrs.get('email')
        password = attrs.get('password')

        # check if credentials are correct
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )

        # if credentials not correct
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')

        # if credentials correct
        # set user attribute to use user in the view
        attrs['user'] = user
        return attrs
