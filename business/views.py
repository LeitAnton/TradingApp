from django.http import Http404
from django.shortcuts import get_list_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from business.models import Currency, Order
from business.serializers import (CreateOrderSerializer, CurrencySerializer,
                                  OrderSerializer, UpdateOrderSerializer)
from user.permissions import IsAnalyst, IsAnAuthor


class CurrencyViewSet(ModelViewSet):
    """ViewSet for the Currency model.

    This ViewSet provides CRUD operations for Currency instances.

    Attributes:
        queryset (QuerySet): The queryset used to fetch Currency objects.
        serializer_class (Serializer): The serializer class for Currency objects.
        default_permission_classes (list): Default permission classes for all actions.
        permission_classes (dict): Permission classes for specific actions.

    """

    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    default_permission_classes = [IsAdminUser, ]

    permission_classes = {
        'list': [IsAuthenticated, ],
        'retrieve': [IsAuthenticated, ],
    }

    def get_permissions(self):
        """Get the appropriate permissions for the current action.

        Returns:
            list: The list of permission classes for the current action.

        """
        return [permission() for permission in
                self.permission_classes.get(self.action, self.default_permission_classes)]


class OrderViewSet(viewsets.GenericViewSet,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.DestroyModelMixin):
    """ViewSet for the Order model.

    This ViewSet provides CRUD operations for Order instances.

    Attributes:
        queryset (QuerySet): The queryset used to fetch Order objects.
        serializer_class (Serializer): The serializer class for Order objects.
        default_permission_classes (list): Default permission classes for all actions.
        permission_classes (dict): Permission classes for specific actions.

    """

    queryset = Order.objects.all()
    default_serializer_class = OrderSerializer
    default_permission_classes = [IsAdminUser, ]

    permission_classes = {
        'list': [IsAnalyst | IsAdminUser],
        'own_orders': [IsAuthenticated, ],
        'create': [IsAuthenticated, ],
        'update': [IsAnAuthor | IsAdminUser],
        'destroy': [IsAnAuthor | IsAdminUser],
        'retrieve': [IsAnAuthor | IsAnalyst | IsAdminUser]
    }
    serializer_classes = {
        'list': OrderSerializer,
        'own_orders': OrderSerializer,
        'create': CreateOrderSerializer,
        'update': UpdateOrderSerializer,
    }

    def get_serializer_class(self):
        """Determine the serializer class based on the action being performed.

        Returns:
           Serializer: The serializer class for the current action.
        """
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    def get_permissions(self):
        """Get the appropriate permissions for the current action.

        Returns:
            list: The list of permission classes for the current action.

        """
        return [permission() for permission in
                self.permission_classes.get(self.action, self.default_permission_classes)]

    def create(self, request, *args, **kwargs):
        """Create a new Order instance.

        Args:
            request (HttpRequest): The incoming HTTP request.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response indicating the status of the creation operation.

        """
        serializer = self.get_serializer_class()(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """Update an existing Order instance.

        Args:
            request (HttpRequest): The incoming HTTP request.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response indicating the status of the update operation.

        """
        order_id = kwargs.get('pk')
        instance = get_object_or_404(Order, id=order_id)
        self.check_object_permissions(request, instance)
        serializer = self.get_serializer_class()(
            request.user, data=request.data, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def own_orders(self, request, *args, **kwargs):
        """Retrieve orders belonging to the authenticated user.

        Args:
            request (HttpRequest): The incoming HTTP request.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response containing the user's orders or an empty list.

        """

        try:
            orders = get_list_or_404(Order, user=request.user)
        except Http404:
            return Response([], status=status.HTTP_200_OK)

        serializers = self.get_serializer_class()(orders, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)
