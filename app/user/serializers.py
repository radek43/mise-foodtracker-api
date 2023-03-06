"""Serializers for the user API view"""
from django.contrib.auth import get_user_model

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
