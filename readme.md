git clone https://github.com/yourname/pc_configurator.git
cd pc_configurator
cp .env.example .env  # настрой при необходимости
docker-compose up --build
➡️ Приложение доступно по адресу: http://localhost:8000
➡️ Админ-панель: http://localhost:8000/admin/dashboard/

# 1. Установи зависимости
pip install -r requirements.txt

# 2. Настрой БД (PostgreSQL)
#    Измени DATABASES в pc_config/settings.py

# 3. Примени миграции
python manage.py migrate

# 4. Заполни БД (опционально)
python manage.py shell < init_local.py

# 5. Запусти сервер
python manage.py runserver
Основные тесты
models.py
forms.py
views.py
admin