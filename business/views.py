from django.http import Http404
from django.shortcuts import get_list_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from business.models import Currency, Order, Subscription, History, Portfolio
from business.serializers import (CreateOrderSerializer, CurrencySerializer,
                                  OrderSerializer, UpdateOrderSerializer, SubscriptionSerializer, SubscribeSerializer,
                                  HistorySerializer, PortfolioSerializer)
from business.tasks import check_orders
from user.models import User
from user.permissions import IsAnalyst, IsAnAuthor


def get_queryset_if_not_a_stuff(some_object, user):
    if user.role not in [User.RolesChoices.ADMIN, User.RolesChoices.ANALYST]:
        queryset = some_object.objects.filter(user=user)
    else:
        queryset = some_object.objects.all()

    return queryset


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
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
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

        check_orders()

        serializers = self.get_serializer_class()(orders, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


class SubscriptionViewSet(viewsets.GenericViewSet,
                          mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          mixins.DestroyModelMixin):
    queryset = Subscription.objects.all()
    default_serializer_class = SubscriptionSerializer
    default_permission_classes = [IsAuthenticated, ]

    permission_classes = {
        'destroy': [IsAnAuthor | IsAdminUser],
    }
    serializer_classes = {
        'create': SubscribeSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    def get_permissions(self):
        return [permission() for permission in
                self.permission_classes.get(self.action, self.default_permission_classes)]

    def list(self, request, *args, **kwargs):
        super().list(request, *args, **kwargs)
        queryset = get_queryset_if_not_a_stuff(Subscription, request.user)

        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class HistoryViewSet(viewsets.GenericViewSet,
                     mixins.ListModelMixin):
    queryset = History.objects.all()
    permission_classes = [IsAuthenticated, ]
    serializer_class = HistorySerializer

    def list(self, request, *args, **kwargs):
        super().list(request, *args, **kwargs)
        queryset = get_queryset_if_not_a_stuff(History, request.user)

        serializer = HistorySerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PortfolioViewSet(viewsets.GenericViewSet,
                       mixins.ListModelMixin):
    queryset = Portfolio.objects.all()
    permission_classes = [IsAuthenticated, ]
    serializer_class = PortfolioSerializer

    def list(self, request, *args, **kwargs):
        super().list(request, *args, **kwargs)
        queryset = Portfolio.objects.filter(user=request.user)

        serializer = PortfolioSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
