"""Serializers for recipe API"""
from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes"""

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'category', 'time_minutes',
                  'calories', 'protein', 'carbs', 'fibers',
                  'fat', 'description', 'ingredients']
        read_only_fields = ['id']
