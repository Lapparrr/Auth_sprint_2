#!/bin/sh


echo "Waiting for Redis..."

while ! nc -z $REDIS_HOST $REDIS_PORT; do
  sleep 1
done

echo "Redis started"


echo "Waiting for PG..."

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 10
done

echo "PG started"

alembic upgrade head

python cli.py create-role admin admin
python cli.py create-role registered default_registered_user
python cli.py create-user $ROOT_LOGIN $ROOT_PASSWORD $ROOT_EMAIL $ROOT_FIRST_NAME $ROOT_LAST_NAME admin


gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app



exec "$@"
