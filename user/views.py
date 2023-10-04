from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from user.models import User
from user.permissions import IsAnalyst
from user.serializers import (ChangePasswordSerializer, LoginSerializer,
                              RegistrationSerializer, ResetPasswordSerializer,
                              UserSerializer)
from user.tasks import send_mail_about_reset_password


class UserViewSet(viewsets.GenericViewSet,
                  mixins.ListModelMixin):
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
        'own_user': UserSerializer,
        'change_password': ChangePasswordSerializer,
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
        'list': [IsAnalyst | IsAdminUser]
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

    @action(detail=False, methods=['patch'])
    def change_password(self, request, *args, **kwargs):
        """Change the user's password.

        Args:
            request (Request): The HTTP request object.
            *args: Variable-length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A response indicating the success of the password change.
        """
        serializer_data = request.data

        serializer = self.get_serializer_class()(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'])
    def reset_password(self, request, *args, **kwargs):
        """Change the user's password.

        Args:
            request (Request): The HTTP request object.
            *args: Variable-length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A response indicating the success of the password change.
        """
        serializer_data = request.data

        serializer = self.get_serializer_class()(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        send_mail_about_reset_password.delay(
            password=serializer.data['password'],
            email=request.user.email
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def own_user(self, request, *args, **kwargs):
        """Retrieve the user's own information.

        Args:
            request (Request): The HTTP request object.
            *args: Variable-length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A response containing the user's information.
        """
        user = get_object_or_404(User, pk=request.user.id)
        serializer = self.get_serializer_class()(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def registration(self, request):
        """Register a new user.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: A response indicating the success of the user registration.
        """
        user = request.data
        serializer = self.get_serializer_class()(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """Log in a user.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: A response indicating the success of the user login.
        """
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def block_user(self, request, *args, **kwargs):
        """Block a user.

        Args:
            request (Request): The HTTP request object.
            *args: Variable-length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A response indicating that the user has been blocked.
        """
        user = get_object_or_404(User, pk=kwargs['pk'])
        user.is_active = False
        user.save()

        return Response({'detail': 'User is block'}, status=status.HTTP_200_OK)
