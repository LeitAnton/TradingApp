#!/bin/sh

until cd /home/TradingApp/web
do
    echo "Waiting for server volume..."
done

celery -A TradingApp beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
