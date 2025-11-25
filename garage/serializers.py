# garage/serializers.py
from rest_framework import serializers
from .models import Car, Service, Mechanic

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class CarSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)
    class Meta:
        model = Car
        fields = '__all__'

class MechanicSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)
    class Meta:
        model = Mechanic
        fields = '__all__'
