#!/bin/sh


echo "Waiting for PG..."

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 10
done

echo "PG started"

python /opt/app/manage.py migrate

uwsgi --strict --ini uwsgi.ini

exec "$@"
