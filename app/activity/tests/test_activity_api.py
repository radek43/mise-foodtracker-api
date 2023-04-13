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

def detail_url(activity_id):
    """Create and return an activity detail URL"""
    return reverse('activity:activity-detail', args=[activity_id])


def create_activity(user, **params):
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
            email='user@example.com',
            password='test1234',
            is_staff=True
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

    def test_get_activity_detail(self):
        """Test get activity detail"""
        activity = create_activity(user=self.user)

        url = detail_url(activity.id)
        res = self.client.get(url)

        serializer = ActivitySerializer(activity)
        self.assertEqual(res.data, serializer.data)

    def test_create_activity(self):
        """Test create an activity"""
        payload = {
            "title": "Alergare",
            "met": Decimal('2.4'),
        }
        res = self.client.post(ACTIVITIES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        activity = Activity.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(activity, k), v)
        self.assertEqual(activity.user, self.user)

    def test_partial_update(self):
        """Test update of a activity"""
        original_met = Decimal('4.3')
        activity = create_activity(
            user=self.user,
            title='Aerobic',
            met=original_met,
        )

        payload = {
            'title': 'Pilates',
        }
        url = detail_url(activity.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        activity.refresh_from_db()
        self.assertEqual(activity.title, payload['title'])
        self.assertEqual(activity.met, original_met)
        self.assertEqual(activity.user, self.user)


    def test_full_update(self):
        """Test update of a activity"""
        activity = create_activity(
            user=self.user,
            title='Aerobic',
            met=Decimal('4.3'),
        )

        payload = {
            'title': 'Plimbare',
            'met': Decimal('2.7'),
        }
        url = detail_url(activity.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        activity.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(activity, k), v)
        self.assertEqual(activity.user, self.user)


    def test_update_user_returns_error(self):
        """Test changing the activity author returns an error"""
        new_user = get_user_model().objects.create_user(
            email='user2@example.com',
            password='test1234',
            is_staff=True,
        )

        activity = create_activity(user=self.user)

        payload = {
            'user': new_user.id,
        }

        url = detail_url(activity.id)
        self.client.patch(url, payload)

        activity.refresh_from_db()
        self.assertEqual(activity.user, self.user)

    def test_delete_activity(self):
        """Test deleting an activity is successful"""
        activity = create_activity(user=self.user)

        url = detail_url(activity.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Activity.objects.filter(id=activity.id).exists())
