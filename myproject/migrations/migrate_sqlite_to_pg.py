#!/usr/bin/env python
"""
Миграция данных из SQLite (db.sqlite3) в PostgreSQL.
Запускать из контейнера web:
$ docker-compose exec web python migrations/migrate_sqlite_to_pg.py
"""
import os
import sqlite3
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from grades.models import GradeRecord

# Подключаемся к старой SQLite
SQLITE_PATH = '/app/db.sqlite3'  # путь внутри контейнера
if not os.path.exists(SQLITE_PATH):
    print("SQLite файл не найден. Пропускаем миграцию.")
    exit()

print("Начинаем миграцию из SQLite в PostgreSQL...")

conn = sqlite3.connect(SQLITE_PATH)
cur = conn.cursor()
cur.execute("SELECT student, subject, grade FROM grades_graderecord")
rows = cur.fetchall()
conn.close()

print(f"Найдено записей: {len(rows)}")

# Сохраняем в PostgreSQL
created = 0
for student, subject, grade in rows:
    try:
        GradeRecord.objects.create(student=student, subject=subject, grade=grade)
        created += 1
    except Exception as e:
        print(f"Ошибка при записи {student}: {e}")

print(f"Успешно перенесено: {created}")