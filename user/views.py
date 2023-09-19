from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .renderers import UserJSONRenderer
from .serializers import (LoginSerializer, RegistrationSerializer,
                          UserSerializer)


class UserViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """ModelViewSet for class User. """

    queryset = User.objects.all()
    # renderer_classes = (UserJSONRenderer,)

    default_serializer_class = UserSerializer
    default_permission_classes = [AllowAny, ]

    serializer_classes = {
        'retrieve': UserSerializer,
        'update': UserSerializer,
        'registration': RegistrationSerializer,
        'login': LoginSerializer,
    }

    permission_classes = {
        'retrieve': [IsAuthenticated],
        'update': [IsAuthenticated],
        'registration': [AllowAny, ],
        'login': [AllowAny],
    }

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    def get_permissions(self):
        return [permission() for permission in
                self.permission_classes.get(self.action, self.default_permission_classes)]

    @action(detail=False, methods=['post'])
    def registration(self, request):
        user = request.data
        serializer = RegistrationSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def login(self, request):
        user = request.data.get('user', {})

        serializer = LoginSerializer(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
