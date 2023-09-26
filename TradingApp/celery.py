import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradingApp.settings')

app = Celery('TradingApp')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

CELERY_BEAT_SCHEDULE = {
    'check_orders': {
        'task': 'business.tasks.check_orders',
        'schedule': crontab(minute="*/10"),
    },
}
