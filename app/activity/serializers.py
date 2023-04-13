"""Serializers for Activity API"""

from rest_framework import serializers
from core.models import Activity


class ActivitySerializer(serializers.ModelSerializer):
    """Serializer for activities"""

    class Meta:
        model = Activity
        fields = ['id', 'title', 'met']
        read_only_fields = ['id']

