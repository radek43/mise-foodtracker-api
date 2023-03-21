"""Tests for food APIs"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Food

from food.serializers import (
    FoodSerializer,
    FoodDetailSerializer,
)


FOODS_URL = reverse('food:food-list')


def detail_url(food_id):
    """Create and return a food detail URL"""
    return reverse('food:food-detail', args=[food_id])


def create_food(user, **params):
    """Create and return a sample food"""
    defaults = {
        'title': 'Sample food title',
        'calories': Decimal('241.2'),
        'carbs': Decimal('36.2'),
        'fibers': Decimal('1'),
        'fat': Decimal('8.3'),
        'protein': Decimal('5.6'),
        'estimates': '1 buc = 254g',
    }
    defaults.update(params)

    food = Food.objects.create(user=user, **defaults)
    return food


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)



class PublicFoodAPITests(TestCase):
    """Test unauthenticated API requests"""
    def setUp(self):
        self.client = APIClient()


    def test_auth_required(self):
        """Test auth is required to call API"""
        res = self.client.get(FOODS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)



class PrivateFoodAPITests(TestCase):
    """Test authenticated API requests"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='email@example.com',
            password='testpass123',
            is_staff=True,
        )
        self.client.force_authenticate(self.user)


    def test_retrieve_foods(self):
        """Test retrieving a list of foods"""
        create_food(user=self.user)
        create_food(user=self.user)

        res = self.client.get(FOODS_URL)

        foods = Food.objects.all().order_by('-id')
        serializer = FoodSerializer(foods, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_get_food_detail(self):
        """Test get food detail"""
        food = create_food(user=self.user)

        url = detail_url(food.id)
        res = self.client.get(url)

        serializer = FoodDetailSerializer(food)
        self.assertEqual(res.data, serializer.data)


    def test_create_food(self):
        """Test creating food"""
        payload = {
            'title': 'Sample food title',
            'calories': Decimal('241.2'),
            'carbs': Decimal('36.2'),
            'fibers': Decimal('1'),
            'fat': Decimal('8.3'),
            'protein': Decimal('5.6'),
        }
        res = self.client.post(FOODS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        food = Food.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(food, k), v)
        self.assertEqual(food.user, self.user)


    def test_partial_update(self):
        """Test partial update of a food"""
        original_carbs = Decimal('36.2')
        food = create_food(
            user=self.user,
            title='Sample food title',
            carbs=original_carbs,
        )
        payload = {
            'title': 'New food title',
        }
        url = detail_url(food.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        food.refresh_from_db()
        self.assertEqual(food.title, payload['title'])
        self.assertEqual(food.carbs, original_carbs)
        self.assertEqual(food.user, self.user)


    def test_full_update(self):
        """Test full update of a food"""
        food = create_food(
            user=self.user,
            title='Sample food title',
            calories=Decimal('241.2'),
            carbs=Decimal('36.2'),
            fibers=Decimal('1'),
            fat=Decimal('8.3'),
            protein=Decimal('5.6'),
        )
        payload = {
            'title': 'New food title',
            'calories': Decimal('2410.2'),
            'carbs': Decimal('360.2'),
            'fibers': Decimal('100'),
            'fat': Decimal('80.3'),
            'protein': Decimal('50.6'),
        }
        url = detail_url(food.id)
        res= self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        food.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(food, k), v)
        self.assertEqual(food.user, self.user)


    def test_update_user_returns_error(self):
        """Test updating a user returns error"""
        new_user = create_user(
            email='user2@example.com',
            password='testpass123',
            is_staff=True,
        )
        food = create_food(user=self.user)

        payload = {
            'user': new_user.id
        }
        url = detail_url(food.id)
        self.client.patch(url, payload)

        food.refresh_from_db()
        self.assertEqual(food.user, self.user)


    def test_delete_food(self):
        """Test delete food is successful"""
        food = create_food(user=self.user)

        url = detail_url(food.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Food.objects.filter(id=food.id).exists())
