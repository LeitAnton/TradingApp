#!/bin/sh
HOST="db"
PORT=5432

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

exec "$@"