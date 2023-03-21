"""Serializers for food APIs"""
from rest_framework import serializers

from core.models import Food


class FoodSerializer(serializers.ModelSerializer):
    """Serializer for foods"""

    class Meta:
        model = Food
        fields = ['id', 'title', 'calories']
        read_only_fields = ['id']

class FoodDetailSerializer(FoodSerializer):
    """Serializer for food detail view"""

    class Meta(FoodSerializer.Meta):
        fields = FoodSerializer.Meta.fields + ['carbs', 'fibers', 'fat', 'protein', 'estimates']
