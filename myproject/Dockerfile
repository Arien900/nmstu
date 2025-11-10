# Stage 1: сборка
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: runtime
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Установка зависимостей
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY . .

# Скрипт ожидания БД
COPY wait-for-db.py /wait-for-db.py

# Сборка статики
RUN python manage.py collectstatic --noinput

CMD ["sh", "-c", "python /wait-for-db.py db:5432 && \
                    python manage.py migrate --noinput && \
                    gunicorn myproject.wsgi:application --bind 0.0.0.0:8000"]