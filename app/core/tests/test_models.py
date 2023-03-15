"""Tests for models"""
from unittest.mock import patch
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email_successful(self):
        """Test creating a user with email is successful"""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users"""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises an ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe is successful"""
        # test user to be assigned to the recipe
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )

        # create test recipe
        recipe = models.Recipe.objects.create(
            user=user,
            title='Hamburger',
            category='Fast-food',
            time_minutes='15',
            calories=Decimal('277.0'),
            protein=Decimal('12.8'),
            carbs=Decimal('0.4'),
            fibers=Decimal('0.0'),
            fat=Decimal('24.9'),
            description='Hamburger Black Angus',
            ingredients='1 Hamburger',
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path"""
        # create a test uuid
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid

        # generate path to uploaded image
        file_path = models.recipe_image_file_path(None, 'example.jpg')

        # check if image is stored in expected path and
        # name matches the uuid
        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
