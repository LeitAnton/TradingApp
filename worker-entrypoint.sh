#!/bin/sh

until cd /home/TradingApp/web
do
    echo "Waiting for server volume..."
done

# run a worker :)
celery -A TradingApp worker --loglevel=info --concurrency 2 -E
celery -A TradingApp worker -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
