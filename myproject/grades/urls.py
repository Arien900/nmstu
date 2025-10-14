from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('save/', views.save_data, name='save'),
    path('upload/', views.upload_file, name='upload'),
    path('list/', views.list_files, name='list'),
    path('export/<str:filename>/', views.export_file, name='export'),
    path('export-combined/<str:ext>/', views.export_combined, name='export_combined'),
]