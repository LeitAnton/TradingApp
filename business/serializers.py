from django.db import IntegrityError
from django.forms import model_to_dict
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

import business.utils
from business.models import Currency, Order, Subscription, History, Portfolio
from user.models import User


class CurrencySerializer(serializers.ModelSerializer):
    """Serializer for the Currency model. """

    class Meta:
        model = Currency
        fields = ('pk', 'title', 'symbol', 'quantity', 'price_per_quantity',)


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for the Order model. """

    class Meta:
        model = Order
        fields = (
            'pk',
            'user',
            'currency',
            'order_type',
            'create_by_price_or_quantity',
            'action',
            'quantity',
            'price',
            'match_price_per_currency_quantity',
        )


class CreateOrderSerializer(OrderSerializer):
    """Serializer for creating Order instances. """
    pk = serializers.IntegerField(read_only=True)
    user = serializers.CharField(allow_null=True, read_only=True)

    def create(self, validated_data):
        """Create a new Order instance. """

        user = self.context['request'].user
        validated_data['user'] = user
        data_after_check_create_by_price_or_quantity = business.utils.check_create_by_price_or_quantity(validated_data)
        data_after_check_order_type = business.utils.check_order_type(data_after_check_create_by_price_or_quantity)

        return Order.objects.create(**data_after_check_order_type)


class UpdateOrderSerializer(OrderSerializer):
    """Serializer for updating Order instances. """
    pk = serializers.IntegerField(read_only=True)
    user = serializers.CharField(allow_null=True, read_only=True)

    def update(self, instance, validated_data):
        """Update an existing Order instance. """

        instance_dict = model_to_dict(instance)
        currency = validated_data.pop('currency', None)

        if currency is None:
            currency = get_object_or_404(Currency, pk=instance_dict['currency'])

        validated_data['user'] = get_object_or_404(User, pk=instance_dict['user'])
        validated_data['currency'] = currency

        for key, value in validated_data.items():
            instance_dict[key] = value

        data_after_check_create_by_price_or_quantity = business.utils.check_create_by_price_or_quantity(instance_dict)
        data_after_check_order_type = business.utils.check_order_type(data_after_check_create_by_price_or_quantity)

        for key, value in data_after_check_order_type.items():
            setattr(instance, key, value)

        instance.save()

        return instance


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('pk', 'user', 'currency')

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        subscription = Subscription.objects.filter(user=validated_data['user'], currency=validated_data['currency'])
        if not subscription:
            return Subscription.objects.create(**validated_data)

        raise IntegrityError('You are already subscribed to this currency. ')


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ('pk', 'user', 'currency', 'action', 'date_time', 'quantity', 'price')


class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ('pk', 'user', 'currency', 'quantity')
