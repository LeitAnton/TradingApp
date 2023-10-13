from django.shortcuts import get_list_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from user.models import User
from user.serializers import (ChangePasswordSerializer, LoginSerializer,
                              RegistrationSerializer, ResetPasswordSerializer,
                              UserSerializer, OwnUserSerializer, AddBalanceToUserSerializer)
from user.permissions import IsAnAuthor


class UserViewSet(viewsets.GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin):
    """ModelViewSet for class User.

    This viewset provides CRUD operations for User objects and additional actions like changing
    passwords, resetting passwords, user registration, and login.

    Attributes:
        queryset (QuerySet): A queryset of User objects.
        default_serializer_class (Serializer): The default serializer class for User objects.
        default_permission_classes (list): The default permission classes for this viewset.

    """

    queryset = User.objects.all()

    default_serializer_class = UserSerializer
    default_permission_classes = [AllowAny, ]

    serializer_classes = {
        'list': OwnUserSerializer,
        'retrieve': OwnUserSerializer,
        'change_password': ChangePasswordSerializer,
        'reset_password': ResetPasswordSerializer,
        'registration': RegistrationSerializer,
        'login': LoginSerializer,
        'add_balance_to_user': AddBalanceToUserSerializer
    }

    permission_classes = {
        'change_password': [IsAuthenticated, ],
        'retrieve': [IsAnAuthor | IsAdminUser ],
        'reset_password': [IsAuthenticated, ],
        'registration': [AllowAny, ],
        'login': [AllowAny, ],
        'block_user': [IsAdminUser, ],
        'list': [IsAuthenticated, ],
        'add_balance_to_user': [IsAdminUser, ]
    }

    def get_serializer_class(self):
        """Determine the serializer class based on the action being performed.

        Returns:
           Serializer: The serializer class for the current action.
        """
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    def get_permissions(self):
        """Determine the permissions required for the current action.

        Returns:
            list: A list of permission classes for the current action.
        """
        return [permission() for permission in
                self.permission_classes.get(self.action, self.default_permission_classes)]

    def get_queryset(self):
        if self.action == 'list':
            if self.request.user.role not in [User.RolesChoices.ADMIN, User.RolesChoices.ANALYST]:
                return User.objects.filter(pk=self.request.user.id)

        return User.objects.all()

    @action(detail=False, methods=['patch'])
    def change_password(self, request, *args, **kwargs):
        """Change the user's password. """
        serializer_data = request.data

        serializer = self.get_serializer_class()(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def reset_password(self, request, *args, **kwargs):
        """Reset the user's password and send it on the mail. """
        serializer_data = request.data

        serializer = self.get_serializer_class()(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({**serializer.data, 'password': 'Check your email to get new password'},
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """Log in a user. """
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def block_user(self, request, *args, **kwargs):
        """Block a user. """
        user = get_object_or_404(User, pk=kwargs['pk'])
        user.is_active = False
        user.save()

        return Response({'detail': 'User is block'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def add_balance_to_user(self, request, *args, **kwargs):
        """Add amount for user's balance. """
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        serializer = self.get_serializer_class()(
            user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def registration(self, request, *args, **kwargs):
        """Register a new user. """
        user = request.data
        serializer = self.get_serializer_class()(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
