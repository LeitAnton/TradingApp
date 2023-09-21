from django_celery_beat.models import PeriodicTask, IntervalSchedule


schedule, created = IntervalSchedule.objects.get_or_create(
    every=1,
    period=IntervalSchedule.SECONDS,
)

PeriodicTask.objects.create(
    interval=schedule,
    name='Check orders',
    task='business.tasks.check_orders',
)
