FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY wait-for-db.py /wait-for-db.py

CMD ["sh", "-c", "\
  python /wait-for-db.py db:5432 && \
  python manage.py migrate --noinput && \
  python manage.py collectstatic --noinput && \
  gunicorn myproject.wsgi:application --bind 0.0.0.0:8000 \
"]