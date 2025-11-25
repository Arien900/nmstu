FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /code

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости системы для psycopg2 и pip-зависимости
RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

# Копируем весь проект
COPY . .

# Экспортируем переменные окружения (чтобы settings.py их использовал)
ENV POSTGRES_DB=auto_center \
    POSTGRES_USER=auto_user \
    POSTGRES_PASSWORD=auto_pass \
    POSTGRES_HOST=db \
    POSTGRES_PORT=5432 \
    DEBUG=1 \
    SECRET_KEY=supersecretkey

# Запуск скрипта ожидания Postgres, а потом старт Django
CMD ["./start.sh"]