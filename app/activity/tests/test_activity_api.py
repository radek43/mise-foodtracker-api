"""Tests for activity API"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Activity

from activity.serializers import (
    ActivitySerializer,
)

ACTIVITIES_URL = reverse('activity:activity-list')

def create_activity(user, *params):
    """Create and return a sample activity"""
    defaults = {
        'title': 'Alergare',
        'met': Decimal('2.4'),
    }
    defaults.update(params)

    activity = Activity.objects.create(user=user, **defaults)
    return activity

class PublicActivityAPITests(TestCase):
    """Test API for unauthenticated users"""

    def setUp(self):
        """Test auth is required to call API"""
        res = self.client.get(ACTIVITIES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateActivityAPITests(TestCase):
    """Test API for authenticated users"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_activities(self):
        """Test retrieving activities"""
        create_activity(user=self.user)
        create_activity(user=self.user)

        res = self.client.get(ACTIVITIES_URL)

        activities = Activity.objects.all().order_by('-id')
        serializer = ActivitySerializer(activities, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
