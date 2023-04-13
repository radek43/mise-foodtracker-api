"""URL mappings for the activity app"""

from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from activity import views


router = DefaultRouter()
router.register('activities', views.ActivityViewSet)

app_name = 'activity'

urlpatterns = [
    path('', include(router.urls)),
]
