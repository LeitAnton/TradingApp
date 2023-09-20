import jwt
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from TradingApp import settings

from .models import User
from .serializers import (LoginSerializer, RegistrationSerializer,
                          ResetPasswordSerializer, UpdateSerializer,
                          UserSerializer)


class UserViewSet(mixins.ListModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """ModelViewSet for class User. """

    queryset = User.objects.all()

    default_serializer_class = UserSerializer
    default_permission_classes = [AllowAny, ]

    serializer_classes = {
        'own_user': UpdateSerializer,
        'change_password': UpdateSerializer,
        'reset_password': ResetPasswordSerializer,
        'registration': RegistrationSerializer,
        'login': LoginSerializer,
    }

    permission_classes = {
        'own_user': [IsAuthenticated, ],
        'change_password': [IsAuthenticated, ],
        'reset_password': [IsAuthenticated, ],
        'registration': [AllowAny, ],
        'login': [AllowAny, ],
        'block_user': [IsAdminUser, ],
    }

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    def get_permissions(self):
        return [permission() for permission in
                self.permission_classes.get(self.action, self.default_permission_classes)]

    @action(detail=False, methods=['put'])
    def change_password(self, request, *args, **kwargs):
        serializer_data = request.data

        serializer = UpdateSerializer(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'])
    def reset_password(self, request, *args, **kwargs):
        serializer_data = request.data

        serializer = ResetPasswordSerializer(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # not_encode_password = serializer.data.serializer.instance.not_encode_password
        # response = dict(serializer.data)
        # response['password'] = not_encode_password

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def own_user(self, request, *args, **kwargs):
        user = User.objects.get(pk=request.user.id)
        return Response({
            'username': user.username,
            'role': user.role
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def registration(self, request):
        user = request.data
        serializer = RegistrationSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def login(self, request):
        user = request.data

        serializer = LoginSerializer(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'])
    def block_user(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs['pk'])
        user.is_active = False
        user.save()

        return Response({'success': 'User is block'}, status=status.HTTP_200_OK)
