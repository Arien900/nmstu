# wait_for_postgres.py
import psycopg2
import time
import os

db_host = os.getenv("POSTGRES_HOST", "db")
db_port = int(os.getenv("POSTGRES_PORT", 5432))
db_name = os.getenv("POSTGRES_DB")
db_user = os.getenv("POSTGRES_USER")
db_pass = os.getenv("POSTGRES_PASSWORD")

while True:
    try:
        conn = psycopg2.connect(
            host=db_host, port=db_port, dbname=db_name, user=db_user, password=db_pass
        )
        conn.close()
        print("Postgres is ready")
        break
    except:
        print("Waiting for Postgres...")
        time.sleep(2)
