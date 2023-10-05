from django.core.management.base import BaseCommand
from business.models import Currency, Order, Subscription
from business.models import User


class Command(BaseCommand):
    help = 'Creating five users, orders, and subscriptions for them.'

    def handle(self, *args, **kwargs):
        currency1 = Currency(
            title='Belarusian ruble',
            symbol='BYN',
            quantity=1,
            price_per_quantity=0.4
        )
        currency1.save()

        currency2 = Currency(
            title='Russian ruble',
            symbol='RUB',
            quantity=100,
            price_per_quantity=1
        )
        currency2.save()

        for i in range(1, 6):
            user = User.objects.create_user(username=f'user{i}',
                                            email=f'anton.lobanov0{i}@gmail.com')
            user.balance = 10000
            user.set_password(f'qwerqwer{i}')
            user.save()

            for currency in (currency1, currency2):
                order1 = Order(
                    user=user,
                    currency=currency,
                    order_type=Order.OrderType.AUTOMATIC,
                    create_by_price_or_quantity=Order.CreateByPriceOrQuantity.PRICE,
                    action=Order.Action.BUY,
                    price=1000,
                    quantity=0,
                    match_price_per_currency_quantity=0.3
                )
                order1.save()

                order2 = Order(
                    user=user,
                    currency=currency,
                    order_type=Order.OrderType.AUTOMATIC,
                    create_by_price_or_quantity=Order.CreateByPriceOrQuantity.PRICE,
                    action=Order.Action.BUY,
                    price=1000,
                    quantity=0,
                    match_price_per_currency_quantity=1.2
                )
                order2.save()

                order3 = Order(
                    user=user,
                    currency=currency,
                    order_type=Order.OrderType.AUTOMATIC,
                    create_by_price_or_quantity=Order.CreateByPriceOrQuantity.PRICE,
                    action=Order.Action.SELL,
                    price=500,
                    quantity=0,
                    match_price_per_currency_quantity=0.3
                )
                order3.save()

                order4 = Order(
                    user=user,
                    currency=currency,
                    order_type=Order.OrderType.AUTOMATIC,
                    create_by_price_or_quantity=Order.CreateByPriceOrQuantity.PRICE,
                    action=Order.Action.SELL,
                    price=500,
                    quantity=0,
                    match_price_per_currency_quantity=1.2
                )
                order4.save()

                order5 = Order(
                    user=user,
                    currency=currency,
                    order_type=Order.OrderType.AUTOMATIC,
                    create_by_price_or_quantity=Order.CreateByPriceOrQuantity.QUANTITY,
                    action=Order.Action.SELL,
                    price=0,
                    quantity=100,
                    match_price_per_currency_quantity=0.3
                )
                order5.save()

                order6 = Order(
                    user=user,
                    currency=currency,
                    order_type=Order.OrderType.AUTOMATIC,
                    create_by_price_or_quantity=Order.CreateByPriceOrQuantity.QUANTITY,
                    action=Order.Action.SELL,
                    price=0,
                    quantity=100,
                    match_price_per_currency_quantity=1.
                )
                order6.save()

                order7 = Order(
                    user=user,
                    currency=currency,
                    order_type=Order.OrderType.MANUAL,
                    create_by_price_or_quantity=Order.CreateByPriceOrQuantity.PRICE,
                    action=Order.Action.BUY,
                    price=1000,
                    quantity=0,
                    match_price_per_currency_quantity=0
                )
                order7.save()

                order8 = Order(
                    user=user,
                    currency=currency,
                    order_type=Order.OrderType.MANUAL,
                    create_by_price_or_quantity=Order.CreateByPriceOrQuantity.PRICE,
                    action=Order.Action.SELL,
                    price=500,
                    quantity=0,
                    match_price_per_currency_quantity=0
                )
                order8.save()

                subscription = Subscription(
                    user=user,
                    currency=currency
                )
                subscription.save()


