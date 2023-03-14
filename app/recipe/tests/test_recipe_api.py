"""Tests for recipe API"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer


RECIPES_URL = reverse('recipe:recipe-list')

def create_recipe(user, **params):
    """Create and return a sample recipe"""

    # default recipe payload
    defaults = {
        'title':'Hamburger',
        'category':'Fast-food',
        'time_minutes':'15',
        'calories':Decimal('277.0'),
        'protein':Decimal('12.8'),
        'carbs':Decimal('0.4'),
        'fibers':Decimal('0.0'),
        'fat':Decimal('24.9'),
        'description':'Hamburger Black Angus',
        'ingredients':'1 Hamburger',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe

class PublicRecipeApiTests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        # create client
        self.client = APIClient()

        def test_auth_required(self):
            """Tests auth is required to call API"""
            res = self.client.get(RECIPES_URL)

            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        # create client
        self.client = APIClient()

        #create user
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        # auth client with the created user
        self.client.force_authenticate(self.user)

    def test_retrive_recipes(self):
        """Test retrieving a list of recipes"""

        # create 2 test recipes
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        # GET request
        res = self.client.get(RECIPES_URL)

        # retrive the recipes from the db
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        # check if db data matches the input
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user"""

        # create another user
        other_user = get_user_model().objects.create_user(
            'otherUser@example.com',
            'password1234',
        )

        # create recipes with different user
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        # send request
        res = self.client.get(RECIPES_URL)

        # filter the result to show only the recipe made by our user
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        # check if data matches
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


