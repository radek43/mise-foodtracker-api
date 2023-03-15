"""Tests for recipe API"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Create and return a recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


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


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


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
        self.user = create_user(email='user@example.com', password='test1234')

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
        other_user = create_user(email='otherUser@example.com', password='password1234')

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


    def test_get_recipe_detail(self):
        """Test get recipe detail"""

        # create recipe
        recipe = create_recipe(user=self.user)

        # pass recipe to API
        url = detail_url(recipe.id)
        res = self.client.get(url)

        # check if data returned correctly
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)


    def test_create_recipe(self):
        """Test creating a recipe"""

        # create payload
        payload = {
            'title': 'Sample Recipe',
            'category': 'Sample Category',
            'time_minutes': 15,
            'calories': Decimal('680.35'),
            'protein': Decimal('18.34'),
            'carbs': Decimal('25.33'),
            'fibers': Decimal('2.31'),
            'fat': Decimal('21.32'),
        }

        # make request
        res = self.client.post(RECIPES_URL, payload)

        # check if response is 'created'
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # retrieve object with id return from the payload
        recipe = Recipe.objects.get(id=res.data['id'])

        # iterate payload to get the objects
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        # check if user assigned to API matches authenticated user
        self.assertEqual(recipe.user, self.user)


    def test_partial_update(self):
        """Test partial update of a recipe"""

        # test variable that checks if the rest of the fields
        # remain the same when making a partial update
        original_time_minutes = 15

        # create a recipe
        recipe = create_recipe(
            user=self.user,
            title='Sample Recipe',
            time_minutes=original_time_minutes,
            calories=Decimal('680.35'),
            protein=Decimal('18.34'),
            carbs=Decimal('25.33'),
            fibers=Decimal('2.31'),
            fat=Decimal('21.32'),
        )

        # payload to update a field in the recipe
        payload = {
            'title': 'NEW Recipe Title'
        }

        # send update request
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        # check if in the result is changed only the title
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, original_time_minutes)
        self.assertEqual(recipe.user, self.user)


    def test_full_update(self):
        """Test full update of a recipe"""

        # create a sample recipe
        recipe = create_recipe(
            user=self.user,
            title='Sample Recipe',
            time_minutes=14,
            calories=Decimal('680.35'),
            protein=Decimal('18.34'),
            carbs=Decimal('25.33'),
            fibers=Decimal('2.31'),
            fat=Decimal('21.32'),
            description='Sample Recipe Description',
            ingredients='Sample Recipe Ingredients',
        )

        # create payload to update the created recipe
        payload = {
            'title': 'New Sample Recipe',
            'category': 'New Sample Category',
            'time_minutes': 24,
            'calories': Decimal('780.35'),
            'protein': Decimal('28.34'),
            'carbs': Decimal('45.33'),
            'fibers': Decimal('5.31'),
            'fat': Decimal('61.32'),
            'description': 'New Sample Recipe Description',
            'ingredients': 'New Sample Recipe Ingredients',
        }

        # make request
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        # check if all the fields from the payload
        # are updated in the created recipe
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)


    def test_update_user_returns_error(self):
        """Test changing the recipe user returns an error"""

        # create a new user
        new_user = create_user(email='user2@example.com', password='test1234')

        # create a recipe with the current user
        # (not the one created earlier)
        recipe = create_recipe(user=self.user)

        # create payload that updates the user field
        payload = {
            'user': new_user.id,
        }

        # make request
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        # check if API prevented the recipe author update
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Check if recipe delete is successful"""

        # create recipe
        recipe = create_recipe(user=self.user)

        # request to delete the created recipe
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        # check if the recipe was deleted from db
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())


    def test_delete_other_users_recipe_error(self):
        """Test trying to delete other user recipe gives error"""

        # create a user
        new_user = create_user(email='test2@example.com', password='test1234')

        # create a recipe with the newly created user
        recipe = create_recipe(user=new_user)

        # make request to delete the other user's recipe
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        # check if the API prevented the deletion
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists)
