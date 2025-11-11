#!/usr/bin/env python
"""
Запускать после первого старта контейнеров:
$ docker compose exec web python migrate_sqlite_to_pg.py
"""
import os
import sqlite3
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from grades.models import GradeRecord

SQLITE_PATH = '/app/db.sqlite3'
if not os.path.exists(SQLITE_PATH):
    print("SQLite не найден. Пропускаем миграцию.")
    exit()

print("Миграция из SQLite → PostgreSQL...")
conn = sqlite3.connect(SQLITE_PATH)
cur = conn.cursor()
cur.execute("SELECT student, subject, grade FROM grades_graderecord")
rows = cur.fetchall()
conn.close()

created = 0
for student, subject, grade in rows:
    try:
        GradeRecord.objects.create(student=student, subject=subject, grade=grade)
        created += 1
    except Exception as e:
        print(f" {student}: {e}")

print(f" Успешно перенесено: {created} записей")