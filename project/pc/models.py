# pc/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.pk:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class User(AbstractUser, TimestampedModel):
    ROLE_CHOICES = [
        ('guest', 'Гость'),
        ('user', 'Пользователь'),
        ('admin', 'Администратор'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest')


class Component(TimestampedModel):
    name = models.CharField(max_length=255, verbose_name="Название")
    category = models.CharField(max_length=100, verbose_name="Категория")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    description = models.TextField(blank=True, verbose_name="Описание")

    # Поля для совместимости
    socket = models.CharField(max_length=100, blank=True, help_text="Сокет (CPU/мат. плата/охлаждение)")
    chipset = models.CharField(max_length=50, blank=True, help_text="Чипсет")
    ram_type = models.CharField(max_length=20, blank=True, choices=[
        ('DDR4', 'DDR4'),
        ('DDR5', 'DDR5'),
    ], help_text="Тип ОЗУ")
    has_pcie = models.BooleanField(default=False, help_text="Есть PCIe x16 (для GPU)")
    power_consumption = models.PositiveIntegerField(default=0, help_text="Потребление, Вт")

    def __str__(self):
        return f"{self.name} ({self.category})"

    def is_compatible_with(self, other):
        """Проверяет совместимость с другим компонентом"""
        # CPU ↔ Мат. плата
        if (self.category == "CPU" and other.category == "Материнская плата") or \
           (self.category == "Материнская плата" and other.category == "CPU"):
            return self.socket and other.socket and self.socket == other.socket

        # ОЗУ ↔ Мат. плата
        if (self.category == "ОЗУ" and other.category == "Материнская плата") or \
           (self.category == "Материнская плата" and other.category == "ОЗУ"):
            return self.ram_type and other.ram_type and self.ram_type == other.ram_type

        # GPU ↔ Мат. плата
        if (self.category == "GPU" and other.category == "Материнская плата") or \
           (self.category == "Материнская плата" and other.category == "GPU"):
            return other.has_pcie if self.category == "GPU" else self.has_pcie

        # CPU ↔ Охлаждение
        if (self.category == "CPU" and other.category == "Охлаждение") or \
           (self.category == "Охлаждение" and other.category == "CPU"):
            cpu_socket = self.socket if self.category == "CPU" else other.socket
            cooler_sockets = (other.socket if self.category == "CPU" else self.socket).split(',')
            return cpu_socket in [s.strip() for s in cooler_sockets]

        return True  # по умолчанию совместимо


class Build(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='builds')
    name = models.CharField(max_length=200)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.name


class BuildComponent(TimestampedModel):
    build = models.ForeignKey(Build, on_delete=models.CASCADE, related_name='components')
    component = models.ForeignKey(Component, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        unique_together = ('build', 'component')


class PresetBuild(TimestampedModel):
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    target = models.CharField(max_length=50, choices=[
        ('gaming', 'Игры'),
        ('office', 'Офис'),
        ('streaming', 'Стриминг'),
        ('budget', 'Бюджет'),
    ], verbose_name="Цель")

    def get_components(self):
        """Возвращает компоненты по шаблону"""
        presets = {
            'gaming': [
                "Intel Core i5-13600K",
                "ASUS ROG Strix B760-G",
                "Kingston Fury Beast 32 ГБ (2×16)",
                "NVIDIA GeForce RTX 4070",
                "Samsung 980 Pro 1 ТБ",
                "Corsair RM850e",
                "DeepCool AK620",
            ],
            'office': [
                "AMD Ryzen 5 7600",
                "MSI PRO B650M-A",
                "Crucial 16 ГБ DDR5",
                "Samsung 970 EVO 500 ГБ",
                "Cooler Master MWE 550",
            ],
            'budget': [
                "Intel Core i3-13100",
                "Gigabyte H610M H",
                "ADATA 8 ГБ DDR4",
                "Intel UHD Graphics 730",
                "Kingston A400 480 ГБ",
                "DeepCool DN450",
            ],
        }
        names = presets.get(self.target, [])
        return Component.objects.filter(name__in=names)

    def __str__(self):
        return f"{self.name} ({self.get_target_display()})"