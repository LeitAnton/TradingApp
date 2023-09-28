from rest_framework import serializers
from business.models import Order


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

    order_type = validated_data['order_type']
    currency = validated_data['currency']

    if order_type == Order.OrderType.MANUAL:
        validated_data['match_price_per_currency_quantity'] = currency.price_per_quantity

    if validated_data['match_price_per_currency_quantity'] is None:
        raise serializers.ValidationError(
            "A match_price_per_currency_quantity is required if order_type is Automatic."
        )

    return validated_data
