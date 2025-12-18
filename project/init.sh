#!/bin/sh
# project/init.sh — запускается при старте web-контейнера

set -e

echo "⏳ Ожидание готовности PostgreSQL..."
while ! nc -z db 5432; do
  sleep 1
done
echo "✅ PostgreSQL готов"

echo "🔧 Применяем миграции..."
python manage.py migrate --noinput

echo "📦 Загружаем компоненты и пресеты..."
python manage.py shell <<EOF
from pc.models import Component, PresetBuild

# Компоненты (без дубликатов)
components = [
    ("Intel Core i5-13600K", "CPU", 25000, "14 ядер, 5.1 ГГц", "LGA1700", "", False, 181),
    ("AMD Ryzen 5 7600", "CPU", 18000, "6 ядер, AM5", "AM5", "", False, 65),
    ("Intel Core i3-13100", "CPU", 10000, "4 ядра, бюджетный", "LGA1700", "", False, 60),
    ("ASUS ROG Strix B760-G", "Материнская плата", 18000, "LGA1700, DDR5", "LGA1700", "DDR5", True, 0),
    ("MSI PRO B650M-A", "Материнская плата", 15000, "AM5, DDR5", "AM5", "DDR5", True, 0),
    ("Gigabyte H610M H", "Материнская плата", 7000, "LGA1700, DDR4", "LGA1700", "DDR4", True, 0),
    ("Kingston Fury Beast 32 ГБ (2×16)", "ОЗУ", 12000, "DDR5, 6000 МГц", "", "DDR5", False, 5),
    ("Crucial 16 ГБ DDR5", "ОЗУ", 6000, "DDR5, 5200 МГц", "", "DDR5", False, 3),
    ("ADATA 8 ГБ DDR4", "ОЗУ", 3000, "DDR4, 3200 МГц", "", "DDR4", False, 2),
    ("NVIDIA GeForce RTX 4070", "GPU", 65000, "12 ГБ VRAM", "", "", False, 200),
    ("Samsung 980 Pro 1 ТБ", "SSD", 10000, "NVMe, PCIe 4.0", "", "", False, 6),
    ("Samsung 970 EVO 500 ГБ", "SSD", 5000, "NVMe, PCIe 3.0", "", "", False, 5),
    ("Kingston A400 480 ГБ", "SSD", 2500, "SATA III", "", "", False, 3),
    ("Corsair RM850e", "БП", 9000, "850 Вт, Gold", "", "", False, 0),
    ("Cooler Master MWE 550", "БП", 5000, "550 Вт, Bronze", "", "", False, 0),
    ("DeepCool DN450", "БП", 3000, "450 Вт", "", "", False, 0),
    ("DeepCool AK620", "Охлаждение", 5000, "Башенный кулер", "LGA1700,AM4,AM5", "", False, 0),
]

for name, cat, price, desc, sock, ram, pcie, power in components:
    Component.objects.get_or_create(
        name=name,
        defaults={
            'category': cat,
            'price': price,
            'description': desc,
            'socket': sock,
            'ram_type': ram,
            'has_pcie': pcie,
            'power_consumption': power
        }
    )
print("✅ 17 компонентов загружено")

# Пресеты
PresetBuild.objects.get_or_create(
    name="Игровая 2025",
    defaults={"description": "Для игр в 1440p", "target": "gaming"}
)
PresetBuild.objects.get_or_create(
    name="Офисная база",
    defaults={"description": "Для работы и Zoom", "target": "office"}
)
PresetBuild.objects.get_or_create(
    name="Бюджетная",
    defaults={"description": "Для учёбы", "target": "budget"}
)
print("✅ 3 пресета загружено")
EOF

echo "👑 Создаём суперпользователя..."
python manage.py shell <<EOF
import os
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username=os.environ['ADMIN_USER']).exists():
    User.objects.create_superuser(
        username=os.environ['ADMIN_USER'],
        email=os.environ['ADMIN_EMAIL'],
        password=os.environ['ADMIN_PASSWORD'],
        role='admin'
    )
    print("✅ Суперпользователь создан")
else:
    print("♻️ Суперпользователь уже существует")
EOF

echo "🚀 Готово! Приложение запущено."