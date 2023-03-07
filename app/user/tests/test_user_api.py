"""Tests for the user API"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


# unauthenticated users
class PublicUserApiTests(TestCase):
    """Test public features of the user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful"""

        # create a user
        payload = {
            'email': 'test@example.com',
            'password': 'test123',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        # check if sent data matches payload
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))

        # check if password is not fetched from db
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists"""

        # user data
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }

        # create user
        create_user(**payload)

        # create user using the api with the same data
        res = self.client.post(CREATE_USER_URL, payload)

        # check if api response returns an error
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is return if password is less than 5 chars"""

        # create user with a password too short
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        # check if api returns error
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # check if user got registered in the database
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generate token for added credentials"""

        # create user
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test-user-pass-123',
        }
        create_user(**user_details)

        # login mock
        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL, payload)

        # check if token created
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid"""

        # create user
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test-user-pass-123',
        }
        create_user(**user_details)

        # login mock with incorrect password
        payload = {
            'email': 'test@example.com',
            'password': 'not-the-users-password',
        }
        res = self.client.post(TOKEN_URL, payload)

        # check if token created
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error"""

        # login mock with blank password
        payload = {
            'email': 'test@example.com',
            'password': '',
        }
        res = self.client.post(TOKEN_URL, payload)

        # check if token created
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users"""
        res = self.client.get(ME_URL)

        # check if returns token if not authenticated
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)



# authenticated users
class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        # auto authenticate before each test
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        # fetch user data
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # check if fetched data is same as authenticated user data
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the ME endpoint"""
        res = self.client.post(ME_URL, {})

        # check if POST works on ME endpoint
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user"""

        # updated user data
        payload = {
            'name': 'Updated Name',
            'password': 'newpass123',
        }
        res = self.client.patch(ME_URL, payload)

        # refresh db to get updated data
        self.user.refresh_from_db()

        # check if fetched data is the same as the data from the payload
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
