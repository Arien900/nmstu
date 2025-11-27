FROM python:3.12-slim

WORKDIR /code

# Устанавливаем только клиент PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["./start.sh"]