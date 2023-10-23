import json
import logging

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from business.tasks import send_message_to_kafka_task


def check_create_by_price_or_quantity(validated_data):
    """Validate and modify order creation data based on 'create_by_price_or_quantity' value.

    This function checks the value of 'create_by_price_or_quantity' in the validated data and ensures
    that the corresponding 'price' or 'quantity' field is set based on the chosen creation method.

    Args:
        validated_data (dict): The validated data containing order creation details.

    Returns:
        dict: The modified validated data with 'quantity' or 'price' set accordingly.

    Raises:
        serializers.ValidationError: If the validation fails (e.g., missing 'price' or 'quantity').

    """
    from business.models import Order

    create_by_price_or_quantity = validated_data['create_by_price_or_quantity']
    currency = validated_data['currency']

    if create_by_price_or_quantity not in [Order.CreateByPriceOrQuantity.PRICE, Order.CreateByPriceOrQuantity.QUANTITY]:
        raise serializers.ValidationError(
            "Create by price or quantity should be equal 'Q' or 'P'. "
        )

    if create_by_price_or_quantity == Order.CreateByPriceOrQuantity.PRICE:
        # If create_by_price_or_quantity is equal to 'P', make sure that 'price' is set.
        if validated_data['price'] is None:
            raise serializers.ValidationError(
                "Price is required when create_by_price_or_quantity is Price."
            )

        validated_data['quantity'] = currency.get_quantity_by_price(validated_data['price'])

    elif create_by_price_or_quantity == Order.CreateByPriceOrQuantity.QUANTITY:
        # If create_by_price_or_quantity is equal to 'Q', make sure that 'quantity' is set.
        if validated_data['quantity'] is None:
            raise serializers.ValidationError(
                "Quantity is required when create_by_price_or_quantity is Quantity."
            )

        validated_data['price'] = currency.get_price_by_quantity(validated_data['quantity'])

    return validated_data


def check_order_type(validated_data):
    """Validate and modify order type data based on 'order_type' value.

    This function checks the value of 'order_type' in the validated data and ensures that the corresponding
    'match_price_per_currency_quantity' field is set based on the chosen order type.

    Args:
        validated_data (dict): The validated data containing order type details.

    Returns:
        dict: The modified validated data with 'match_price_per_currency_quantity' set accordingly.

    Raises:
        serializers.ValidationError: If the validation fails (e.g., missing 'match_price_per_currency_quantity').

    """
    from business.models import Order

    order_type = validated_data['order_type']
    currency = validated_data['currency']

    if order_type == Order.OrderType.MANUAL:
        validated_data['match_price_per_currency_quantity'] = currency.price_per_quantity

    if validated_data['match_price_per_currency_quantity'] is None:
        raise serializers.ValidationError(
            "A match_price_per_currency_quantity is required if order_type is Automatic."
        )

    return validated_data


def send_action_currency(action, symbol):
    topic_currency_action = 'topic_currency_action'
    message = {
        'action': action,
        'symbol': symbol,
    }
    send_message_to_kafka_task(topic_currency_action, message)


def send_currencies():
    from business.models import Currency
    currencies = Currency.objects.all().values_list('symbol')
    topic_get_currencies = 'topic_get_currencies'
    message = {
        'currencies': currencies,
    }
    send_message_to_kafka_task(topic_get_currencies, message)


def update_currency_in_database(data):
    from business.models import Currency
    try:
        serializer_data = json.loads(data)
        symbol = serializer_data['symbol']

        currency = get_object_or_404(Currency, symbol=symbol)
        currency.price_per_quantity = serializer_data['price']
        currency.save()
    except Exception as error:
        logging.error(msg=f'Error updating currency in database: {error}')
