# Dockerfile
FROM python:3.11-slim

# Установим зависимости ОС: netcat, gettext (для envsubst), ca-certificates
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        netcat-openbsd \
        gettext \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY project/ .

RUN chmod +x /app/init.sh

CMD ["/app/init.sh"]