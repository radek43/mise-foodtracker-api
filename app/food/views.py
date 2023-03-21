"""Views for the food APIs"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from auth import custom_permissions

from core.models import Food

from food import serializers


class FoodViewSet(viewsets.ModelViewSet):
    """View for manage food APIs"""
    serializer_class = serializers.FoodDetailSerializer
    queryset = Food.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [custom_permissions.UserPermission]

    def get_queryset(self):
        """Retrieve recipes for authenticated user"""
        return self.queryset.order_by('-id')

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.FoodSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create new food"""
        serializer.save(user=self.request.user)
