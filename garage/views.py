# garage/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Car, Service, Mechanic
from .serializers import CarSerializer, ServiceSerializer, MechanicSerializer

class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [IsAuthenticated]

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

class MechanicViewSet(viewsets.ModelViewSet):
    queryset = Mechanic.objects.all()
    serializer_class = MechanicSerializer
    permission_classes = [IsAuthenticated]
