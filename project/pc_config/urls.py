from django.contrib import admin
from django.urls import path, include
from pc import views

urlpatterns = [
    path('', include('pc.urls')),
]