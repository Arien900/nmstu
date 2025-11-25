#!/bin/sh
# Ждем пока Postgres будет готов
python wait_for_postgres.py

# Запускаем Django сервер
exec python manage.py runserver 0.0.0.0:8000
