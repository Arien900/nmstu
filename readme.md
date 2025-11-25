1. Клонируем репозиторий
2. Создаем и запускаем контейнер docker-compose up --build
3. Мигрируем данные docker-compose exec backend python manage.py migrate
4. Создание пользователя docker-compose exec backend python manage.py createsuperuser
5. Доступ к серверу http://localhost:8000/swagger/
Получение токена
POST /api/token/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}