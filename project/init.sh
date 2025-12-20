#!/bin/sh
set -e

echo "⏳ Ожидание PostgreSQL..."
while ! nc -z db 5432; do
  sleep 1
done
echo "✅ PostgreSQL готов"

echo "🔧 Создаём миграции для приложения 'pc'..."
python manage.py makemigrations pc --no-input

echo "🚀 Применяем миграции..."
python manage.py migrate --noinput

echo "📦 Загружаем компоненты..."
python manage.py shell << 'EOF'
from pc.models import Component as C

data = [
    ("Intel Core i5-13600K", "CPU", 25000, "LGA1700", "", False),
    ("AMD Ryzen 5 7600", "CPU", 18000, "AM5", "", False),
    ("ASUS ROG Strix B760-G", "МП", 18000, "LGA1700", "DDR5", True),
    ("MSI PRO B650M-A", "МП", 15000, "AM5", "DDR5", True),
    ("Kingston Fury Beast 32 ГБ", "ОЗУ", 12000, "", "DDR5", False),
    ("Samsung 980 Pro 1 ТБ", "SSD", 10000, "", "", False),              
    ("Corsair RM850e", "БП", 8000, "", "", False),                        
    ("DeepCool AK620", "Охлаждение", 3000, "LGA1700,AM4", "", False),   
    ("NVIDIA GeForce RTX 4070", "GPU", 65000, "", "", True),
]

for name, cat, price, socket, ram_type, has_pcie in data:
    obj, created = C.objects.get_or_create(
        name=name,
        defaults={
            "category": cat,
            "price": price,
            "socket": socket,
            "ram_type": ram_type,
            "has_pcie": has_pcie
        }
    )
    if created:
        print("  ➕", name)
    else:
        print("  ♻️", name, "(уже есть)")
EOF

echo "👑 Создаём суперпользователя..."
python manage.py shell << 'EOF'
from pc.models import User
from django.contrib.auth.hashers import make_password

username = "admin"
email = "admin@example.com"
raw_password = "admin123"  # ← меняй в .env в будущем

user, created = User.objects.get_or_create(
    username=username,
    defaults={
        "email": email,
        "role": "admin",
        "is_staff": True,
        "is_superuser": True,
        "password": make_password(raw_password)
    }
)
if created:
    print("✅ Админ создан. Логин:", username, "| Пароль:", raw_password)
else:
    print("♻️ Админ уже существует.")
EOF

echo "✅ Инициализация завершена. Запускаем сервер..."
exec gunicorn pc_config.wsgi:application --bind 0.0.0.0:8000 --workers 2