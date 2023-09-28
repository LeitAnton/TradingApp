from django.db import IntegrityError
from rest_framework import serializers

import business.utils
from business.models import Currency, Order, Portfolio


class CurrencySerializer(serializers.ModelSerializer):
    """Serializer for the Currency model.

    This serializer is used to serialize Currency objects.

    """

    class Meta:
        model = Currency
        fields = ('pk', 'title', 'symbol', 'quantity', 'price_per_quantity',)


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for the Order model.

    This serializer is used to serialize Order objects.

    """

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


class CreateOrderSerializer(serializers.ModelSerializer):
    """Serializer for creating Order instances.

    This serializer is used for creating Order objects, including validation and processing of data.

    Attributes:
        user (CharField): The user creating the order (read-only).
        price (FloatField): The price for the order.
        quantity (FloatField): The quantity for the order.
        match_price_per_currency_quantity (FloatField): The match price per currency quantity.

    """

    user = serializers.CharField(allow_null=True, read_only=True)
    price = serializers.FloatField(allow_null=True)
    quantity = serializers.FloatField(allow_null=True)
    match_price_per_currency_quantity = serializers.FloatField(allow_null=True)

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
        read_only = ('user',)

    def create(self, validated_data):
        """Create a new Order instance.

        Args:
            validated_data (dict): The validated data for order creation.

        Returns:
            Order: The newly created Order instance.

        """

        user = self.context['request'].user
        validated_data['user'] = user
        data = business.utils.check_create_by_price_or_quantity(validated_data)
        data = business.utils.check_order_type(data)

        return Order.objects.create(**data)


class UpdateOrderSerializer(serializers.ModelSerializer):
    """Serializer for updating Order instances.

    This serializer is used for updating existing Order objects, including validation and processing of data.

    """

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
        read_only = ('user',)

    def update(self, instance, validated_data):
        """Update an existing Order instance.

        Args:
            instance (Order): The existing Order instance to update.
            validated_data (dict): The validated data for order update.

        Returns:
            Order: The updated Order instance.

        """

        user = self.context['request'].user
        validated_data['user'] = user
        data = business.utils.check_create_by_price_or_quantity(validated_data)
        data = business.utils.check_order_type(data)

        for key, value in data.items():
            setattr(instance, key, value)

        instance.save()

        return instance


class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ('pk', 'user', 'currency')


class AddToPortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ('pk', 'user', 'currency')

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        portfolio = Portfolio.objects.filter(user=validated_data['user'], currency=validated_data['currency'])
        if not portfolio:
            return Portfolio.objects.create(**validated_data)

        raise IntegrityError('This currency is already exist in your portfolio. ')
