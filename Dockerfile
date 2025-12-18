FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends netcat-openbsd && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем ВСЁ после установки зависимостей
COPY project/ .

RUN chmod +x init.sh

CMD ["sh", "-c", "./init.sh && gunicorn pc_config.wsgi:application --bind 0.0.0.0:8000"]