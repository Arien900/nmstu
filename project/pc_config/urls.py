# pc_config/urls.py
from django.contrib import admin
from django.urls import path, include
from pc import views

urlpatterns = [
    path('admin/', admin.site.urls),  # ← ОБЯЗАТЕЛЬНО ДОБАВЬ ЭТУ СТРОКУ

    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('presets/', views.presets_view, name='presets'),
    path('presets/use/<int:preset_id>/', views.use_preset_view, name='use_preset'),
    path('build/create/', views.create_build_view, name='create_build'),
    path('export/', views.export_view, name='export'),
]