#!/bin/sh
HOST=${HOST}
PORT=${PORT}

if [ "$POSTGRES_DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $HOST $PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

echo "Ok"

python3 manage.py migrate
# python3 manage.py create_models
python3 manage.py run_currencies_updating

exec "$@"