"""Views for the user API"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """Create a new user in system"""

    # override default serializer
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""

    # override default serializer
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    """Manage authenticated users"""

    # override default serializer
    serializer_class = UserSerializer

    # set token authentication
    authentication_classes = [authentication.TokenAuthentication]

    # user must be authenticated to use this API
    permission_classes = [permissions.IsAuthenticated]

    # override get_object
    def get_object(self):
        """Retrieve and return the authenticated user"""
        return self.request.user
