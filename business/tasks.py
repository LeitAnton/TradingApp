from celery import shared_task
from django.core.mail import send_mail
from django.db import transaction
from rest_framework.generics import get_object_or_404

from TradingApp.celery import app
from business.models import Order, History, Portfolio


@shared_task
def check_orders():
    orders = Order.objects.all()
    for order in orders:
        close_order.delay(order.pk)


@app.task
@transaction.atomic
def close_order(order_id):
    order = get_object_or_404(Order, pk=order_id)
    if order.check_match_price():
        order.recalculation_of_price_or_quantity()
        portfolio = Portfolio.objects.get_or_create(user=order.user, currency=order.currency)[0]

        if (order.quantity > portfolio.quantity and order.action == Order.Action.SELL
                or order.user.balance < order.price and order.order_type == Order.Action.BUY):
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
def send_mail_about_insufficient_funds(order, email):
    send_mail(
        subject='Insufficient funds',
        message=f"""There are insufficient funds in the account. Order was delete.
                    Order: {order}""",
        from_email=None,
        recipient_list=[email],
        fail_silently=False
    )
