from business.models import Order, History
from celery import shared_task
from TradingApp.celery import app
from django.core.mail import send_mail


@shared_task
def check_orders():
    orders = Order.objects.all()
    for order in orders:
        close_order.delay(order)


@app.task
def close_order(order):
    if order.check_match_price():
        order.recalculation_of_price_or_quantity()
        history = History.objects.create(
            user=order.user,
            currency=order.currency,
            action=order.action,
            quantity=order.quantity,
            price=order.price
        )
        history.save()

        send_mail_about_closed_order.delay(
            subject="Order close",
            message=f"""Your order {order} closed.
                        View your order history for more details. """,
            email=[order.user.email],
        )
        order.delete()


@app.task
def send_mail_about_closed_order(subject, message, email):
    send_mail(
        subject=subject,
        message=message,
        from_email=None,
        recipient_list=[email],
        fail_silently=False
    )
