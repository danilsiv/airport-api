from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, AuthTokenSerializer


@extend_schema(
    summary="Create user",
    description="This endpoint allows users to register by providing necessary credentials."
)
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = ()


@extend_schema(
    summary="Login user",
    description="Authenticates user and returns a token for further API access."
)
class LoginUserView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
