
Требования

- Docker 20.10+
- Docker Compose v2.10+

Запуск

1. Скачайте докер и соберите контейнер docker-compose up --build
2. Дождитесь окончания
3. Откройте ссылку 127.0.0.1:8000
Для миграции с SQLite используйте docker-compose exec web python migrate_sqlite_to_pg.py
Записи в БД docker-compose exec db psql -U grades_user -d grades_db -c "select * from grades_graderecord;"
