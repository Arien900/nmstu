FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY project/ .

CMD ["gunicorn", "pc_config.wsgi:application", "--bind", "0.0.0.0:8000"]