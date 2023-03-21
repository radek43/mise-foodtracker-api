"""URL mappings for food API"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from food import views


router = DefaultRouter()
router.register('foods', views.FoodViewSet)

app_name = 'food'

urlpatterns = [
    path('', include(router.urls)),
]
