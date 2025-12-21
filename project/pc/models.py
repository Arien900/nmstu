from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# Абстрактная модель
class TimestampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.pk:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


# Кастомный пользователь с ролями
class User(AbstractUser, TimestampedModel):
    ROLE_CHOICES = [
        ('guest', 'Гость'),
        ('user', 'Пользователь'),
        ('admin', 'Админ'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest')


# Компонент ПК
class Component(TimestampedModel):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50)
    price = models.IntegerField()
    description = models.TextField(blank=True)   
    socket = models.CharField(max_length=50, blank=True)
    chipset = models.CharField(max_length=50, blank=True) 
    ram_type = models.CharField(max_length=10, blank=True)
    has_pcie = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.name} ({self.category})"           

    # Проверка совместимости
    def is_compatible_with(self, other):
        if {self.category, other.category} == {"CPU", "МП"}:
            return self.socket == other.socket
        if {self.category, other.category} == {"ОЗУ", "МП"}:
            return self.ram_type == other.ram_type
        if {self.category, other.category} == {"GPU", "МП"}:
            return other.has_pcie
        return True 


# Сборка пользователя
class Build(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='builds')
    name = models.CharField(max_length=100)
    total_price = models.IntegerField()

    class Meta:
        unique_together = ('user', 'name') 


# Связь сборки и компонентов
class BuildComponent(TimestampedModel):
    build = models.ForeignKey(
        Build, 
        on_delete=models.CASCADE,
        related_name='components'  
    )
    component = models.ForeignKey(Component, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField(default=1)


# Готовая сборка 
class PresetBuild(TimestampedModel):
    name = models.CharField(max_length=100)
    target = models.CharField(max_length=20, choices=[('gaming', 'Игры'), ('office', 'Офис')])

    # Возвращает компоненты по ключевым словам 
    def get_components(self):
        from django.db.models import Q
        keywords = {
            'gaming': ['i5', 'B760', 'DDR5', 'RTX'],
            'office': ['Ryzen', 'B650', 'DDR5'],
        }
        q = Q()
        for kw in keywords.get(self.target, []):
            q |= Q(name__icontains=kw)
        return Component.objects.filter(q)