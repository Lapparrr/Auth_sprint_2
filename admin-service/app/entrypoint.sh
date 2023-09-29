#!/bin/sh


echo "Waiting for PG..."

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 10
done

echo "PG started"

uwsgi --strict --ini uwsgi.ini

exec "$@"
