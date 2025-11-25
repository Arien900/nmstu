#!/bin/sh
# wait-for-db.sh

set -e

echo "Waiting for postgres..."

until nc -z $DB_HOST $DB_PORT; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "Postgres is up - running migrations"
python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
