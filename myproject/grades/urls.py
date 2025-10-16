from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_files, name='home'),
    path('list/', views.list_files, name='list'),  # ← добавили
    path('save/', views.save_data, name='save'),
    path('upload/', views.upload_file, name='upload'),
    path('export-all/', views.export_all, name='export_all'),
]