# garage/models.py
from django.db import models
from django.contrib.auth.models import User

class Car(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cars')
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.make} {self.model} ({self.year})"


class Service(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='services')
    description = models.TextField()
    date = models.DateField(auto_now_add=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.car} - {self.description}"


class Mechanic(models.Model):
    name = models.CharField(max_length=100)
    services = models.ManyToManyField(Service, related_name='mechanics')

    def __str__(self):
        return self.name
