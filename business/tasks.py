from business.models import Order, History
from celery import shared_task


@shared_task
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
        order.delete()
        # TODO send message for user about order close


@shared_task
def check_orders():
    orders = Order.objects.all()
    for order in orders:
        close_order.delay(order)
