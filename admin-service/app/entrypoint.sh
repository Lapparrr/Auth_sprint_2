#!/bin/sh


echo "Waiting for PG..."

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 10
done

echo "PG started"



uwsgi --strict --ini uwsgi.ini

exec "$@"
