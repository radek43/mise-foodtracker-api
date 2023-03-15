"""Serializers for recipe API"""
from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes"""

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'calories' ]
        read_only_fields = ['id']


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['category', 'time_minutes',
                                                 'protein', 'carbs', 'fibers',
                                                 'fat', 'description',
                                                 'ingredients']

