from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from business.models import Currency, Order, Subscription, History, Portfolio
from business.serializers import (CreateOrderSerializer, CurrencySerializer,
                                  OrderSerializer, UpdateOrderSerializer, SubscriptionSerializer,
                                  HistorySerializer, PortfolioSerializer)
from user.models import User
from user.permissions import IsAnalyst, IsAnAuthor


def get_own_if_not_a_stuff(user, some_object):
    if user.role not in [User.RolesChoices.ADMIN, User.RolesChoices.ANALYST]:
        return some_object.objects.filter(user=user)

    return some_object.objects.all()


class CurrencyViewSet(ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    default_permission_classes = [IsAdminUser, ]

    permission_classes = {
        'list': [IsAuthenticated, ],
        'retrieve': [IsAuthenticated, ],
    }

    def get_permissions(self):
        return [permission() for permission in
                self.permission_classes.get(self.action, self.default_permission_classes)]


class OrderViewSet(viewsets.GenericViewSet,
                   mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin):
    queryset = Order.objects.all()
    default_serializer_class = OrderSerializer
    default_permission_classes = [IsAdminUser, ]

    permission_classes = {
        'list': [IsAuthenticated, ],
        'create': [IsAuthenticated, ],
        'update': [IsAnAuthor | IsAdminUser],
        'destroy': [IsAnAuthor | IsAdminUser],
        'retrieve': [IsAnAuthor | IsAnalyst | IsAdminUser]
    }
    serializer_classes = {
        'list': OrderSerializer,
        'create': CreateOrderSerializer,
        'update': UpdateOrderSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    def get_permissions(self):
        return [permission() for permission in
                self.permission_classes.get(self.action, self.default_permission_classes)]

    def get_queryset(self):
        if self.action == 'list':
            return get_own_if_not_a_stuff(self.request.user, Order)

        return Order.objects.all()


class SubscriptionViewSet(viewsets.GenericViewSet,
                          mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          mixins.DestroyModelMixin):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    default_permission_classes = [IsAuthenticated, ]

    permission_classes = {
        'destroy': [IsAnAuthor | IsAdminUser],
    }

    def get_queryset(self):
        if self.action == 'list':
            return get_own_if_not_a_stuff(self.request.user, Subscription)

        return Subscription.objects.all()

    def get_permissions(self):
        return [permission() for permission in
                self.permission_classes.get(self.action, self.default_permission_classes)]


class HistoryViewSet(viewsets.GenericViewSet,
                     mixins.ListModelMixin):
    queryset = History.objects.all()
    permission_classes = [IsAuthenticated, ]
    serializer_class = HistorySerializer

    def get_queryset(self):
        if self.action == 'list':
            return get_own_if_not_a_stuff(self.request.user, History)

        return History.objects.all()


class PortfolioViewSet(viewsets.GenericViewSet,
                       mixins.ListModelMixin):
    queryset = Portfolio.objects.all()
    permission_classes = [IsAuthenticated, ]
    serializer_class = PortfolioSerializer

    def get_queryset(self):
        if self.action == 'list':
            return get_own_if_not_a_stuff(self.request.user, Portfolio)

        return Portfolio.objects.all()
