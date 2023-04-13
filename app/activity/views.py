"""Views for Activity API"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from auth import custom_permissions

from core.models import Activity
from activity import serializers


class ActivityViewSet(viewsets.ModelViewSet):
    """View for managing activity APIs"""
    serializer_class = serializers.ActivitySerializer
    queryset = Activity.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [custom_permissions.UserPermission]

    def get_queryset(self):
        """Retrieve activities"""
        return self.queryset.order_by('-id')

    def perform_create(self, serializer):
        """Create a new activity"""
        serializer.save(user=self.request.user)
