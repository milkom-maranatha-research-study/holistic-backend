#!/bin/bash

PG_HOST="postgres"
PG_PORT="5432"
TIMEOUT="60"

until nc -w $TIMEOUT -z $PG_HOST $PG_PORT; do
    echo "Connection to ${PG_HOST}:${PG_PORT} was failed"
    sleep 1
done

python manage.py migrate
python manage.py runserver 0.0.0.0:8080
