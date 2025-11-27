from django.contrib import admin
from .models import Car, Service, Mechanic

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'year', 'owner')
    list_filter = ('year', 'owner')
    search_fields = ('make', 'model', 'owner__username')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('description', 'car', 'date', 'cost')
    list_filter = ('date', 'car__make')
    search_fields = ('description',)

@admin.register(Mechanic)
class MechanicAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

    # Чтобы видеть связанные услуги в админке механика
    filter_horizontal = ('services',)  # ← важно для ManyToMany!