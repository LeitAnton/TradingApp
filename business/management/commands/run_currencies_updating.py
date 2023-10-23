from django.core.management.base import BaseCommand

from business.models import Currency
from business.tasks import send_message_to_kafka_task, run_currencies_updating


class Command(BaseCommand):
    help = 'Creating five users, orders, and subscriptions for them.'

    def handle(self, *args, **kwargs):
        topic_get_currencies = 'topic_get_currencies'
        symbols = list(Currency.objects.values_list('symbol', flat=True))
        send_message_to_kafka_task.delay(topic_get_currencies, {'symbols': symbols})

        run_currencies_updating.delay()
