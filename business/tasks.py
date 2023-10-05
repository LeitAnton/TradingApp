from celery import shared_task
from django.core.mail import send_mail
from django.db import transaction
from rest_framework.generics import get_object_or_404

from TradingApp.celery import app


@shared_task
def check_orders():
    from business.models import Order
    orders = Order.objects.all()
    for order in orders:
        close_order.delay(order.pk)


@app.task
@transaction.atomic
def close_order(order_id):
    from business.models import History, Portfolio, Order
    order = get_object_or_404(Order, pk=order_id)
    try:
        if order.order_type == Order.OrderType.MANUAL:
            order.match_price_per_currency_quantity = order.currency.price_per_quantity
            order.save()

        if order.check_match_price():
            order.recalculation_of_price_or_quantity()
            portfolio = Portfolio.objects.get_or_create(user=order.user, currency=order.currency)[0]

            if ((order.quantity > portfolio.quantity and order.action == Order.Action.SELL)
                    or (order.user.balance < order.price and order.action == Order.Action.BUY)):
                send_mail_about_insufficient_funds.delay(str(order), order.user.email)
                order.delete()
                return 'Insufficient funds'

            if order.action == Order.Action.BUY:
                order.user.balance -= order.price
                portfolio.quantity += order.quantity

            if order.action == Order.Action.SELL:
                order.user.balance += order.price
                portfolio.quantity -= order.quantity

            history = History.objects.create(
                user=order.user,
                currency=order.currency,
                action=order.action,
                quantity=order.quantity,
                price=order.price
            )

            send_mail_about_order_close.delay(str(order), order.user.email)

            history.save()
            portfolio.save()
            order.user.save()
            order.delete()

            return 'Order was close'
        else:
            return "The price didn't match"
    except Exception:
        send_mail_about_transaction_error.delay(str(order), order.user.email)
        return 'An error occurred during the transaction.'


@app.task
def send_mail_about_order_close(order, email):
    send_mail(
        subject='Order close',
        message=f"""Your order {order} closed.
                    View your order history for more details. """,
        from_email=None,
        recipient_list=[email],
        fail_silently=False
    )


@app.task
def send_mail_about_transaction_error(order, error, email):
    send_mail(
        subject='Order wasn\'t close',
        message=f"""Your order {order} wasn\'t close.
                    An error occurred during the transaction. """,
        from_email=None,
        recipient_list=[email],
        fail_silently=False
    )


@app.task
def send_mail_about_insufficient_funds(order, email):
    send_mail(
        subject='Insufficient funds',
        message=f"""There are insufficient funds in the account. Order was delete.
                    Order: {order}""",
        from_email=None,
        recipient_list=[email],
        fail_silently=False
    )
