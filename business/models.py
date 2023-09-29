from django.db import models

from user.models import User


class Currency(models.Model):
    """Model representing a currency.

    This model stores information about a currency, including its title, symbol, quantity, and price per quantity.

    Attributes:
        title (str): The title or name of the currency.
        symbol (str): The symbol or abbreviation of the currency.
        quantity (float): The quantity of the currency.
        price_per_quantity (float): The price per quantity of the currency.

    """

    title = models.CharField(max_length=255, unique=True)
    symbol = models.CharField(max_length=3, unique=True)
    quantity = models.FloatField()
    price_per_quantity = models.FloatField()

    def __str__(self):
        return f'{self.title}'

    def get_price_by_quantity(self, quantity):
        """Calculate the price based on a given quantity.

        Args:
            quantity (float): The quantity for which to calculate the price.

        Returns:
            float: The calculated price.

        """
        modifier = quantity / self.quantity
        return self.price_per_quantity * modifier

    def get_quantity_by_price(self, price):
        """Calculate the quantity based on a given price.

        Args:
            price (float): The price for which to calculate the quantity.

        Returns:
            float: The calculated quantity.

        """
        modifier = price / self.price_per_quantity
        return modifier * self.quantity


class Order(models.Model):
    """Model representing an order.

    This model stores information about an order, including the user, currency, order type, creation method, action,
    quantity, price, and match price per currency quantity.

    Attributes:
        user (ForeignKey): The user associated with the order.
        currency (ForeignKey): The currency associated with the order.
        order_type (str): The type of the order (Automatic or Manual).
        create_by_price_or_quantity (str): The method used to create the order (Price or Quantity).
        action (str): The action associated with the order (Buy or Sell).
        quantity (float): The quantity of the order.
        price (float): The price of the order.
        match_price_per_currency_quantity (float): The match price per currency quantity.

    """

    class Action(models.TextChoices):
        BUY = 'B', 'Buy'
        SELL = 'S', 'Sell'

    class OrderType(models.TextChoices):
        AUTOMATIC = 'A', 'Automatic'
        MANUAL = 'M', 'Manual'

    class CreateByPriceOrQuantity(models.TextChoices):
        PRICE = 'P', 'Price'
        QUANTITY = 'Q', 'Quantity'

    user = models.ForeignKey(User, models.CASCADE)
    currency = models.ForeignKey(Currency, models.CASCADE)
    order_type = models.CharField(
        max_length=1,
        choices=OrderType.choices,
        default=OrderType.MANUAL
    )
    create_by_price_or_quantity = models.CharField(
        max_length=1,
        choices=CreateByPriceOrQuantity.choices
    )
    action = models.CharField(
        max_length=1,
        choices=Action.choices
    )
    quantity = models.FloatField(default=0.0)
    price = models.FloatField(default=0.0)
    match_price_per_currency_quantity = models.FloatField(default=0.0)

    def __str__(self):
        return (f"Username: {self.user.username} "
                f"| {self.quantity} {self.currency.symbol} -- {self.price} USD "
                f"| Action: {self.action}"
                f"| Match price: {self.match_price_per_currency_quantity} | Currency price "
                f"| {self.currency.price_per_quantity}")

    def recalculation_of_price_or_quantity(self):
        if self.create_by_price_or_quantity.upper() == self.CreateByPriceOrQuantity.PRICE:
            self.quantity = self.price * self.currency.quantity / self.currency.price_per_quantity

        if self.create_by_price_or_quantity.upper() == self.CreateByPriceOrQuantity.QUANTITY:
            self.price = self.quantity * self.currency.price_per_quantity / self.currency.quantity

    def check_match_price(self) -> bool:
        """Check if the match price per currency quantity matches the currency's price and action.

        Returns:
            bool: True if the match conditions are met, False otherwise.

        """
        if (self.match_price_per_currency_quantity >= self.currency.price_per_quantity
                and self.action == self.Action.SELL):
            return True

        if (self.match_price_per_currency_quantity <= self.currency.price_per_quantity
                and self.action == self.Action.BUY):
            return True

        return False


class History(models.Model):
    """Model representing a transaction history entry.

    This model stores information about a transaction history entry, including the user, currency, action,
    date and time, quantity, and price.

    Attributes:
        user (ForeignKey): The user associated with the history entry.
        currency (ForeignKey): The currency associated with the history entry.
        action (str): The action associated with the history entry (Buy or Sell).
        date_time (DateTimeField): The date and time of the history entry.
        quantity (float): The quantity of the transaction.
        price (float): The price of the transaction.

    """

    class Action(models.TextChoices):
        BUY = 'B', 'Buy'
        SELL = 'S', 'Sell'

    user = models.ForeignKey(User, models.SET_NULL, null=True)
    currency = models.ForeignKey(Currency, models.SET_NULL, null=True)
    action = models.CharField(max_length=1, choices=Action.choices)
    date_time = models.DateTimeField(auto_now=True)
    quantity = models.FloatField()
    price = models.FloatField()

    def __str__(self):
        return (f"Username: {self.user.username} "
                f"| {self.quantity} {self.currency.symbol} -- {self.price} USD "
                f"| Action: {self.action}")


class Subscription(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    currency = models.ForeignKey(Currency, models.CASCADE, related_name='subscriptions')

    def __str__(self):
        return f'User: {self.user.username} -- Currency: {self.currency}'


class Portfolio(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    currency = models.ForeignKey(Currency, models.CASCADE)
    quantity = models.FloatField(default=0.0)
