from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_files, name='home'),
    path('save/', views.save_data, name='save'),
    path('upload/', views.upload_file, name='upload'),
    path('api/search/', views.search_records, name='search'),
    path('api/edit/<int:pk>/', views.edit_record, name='edit'),
    path('api/delete/<int:pk>/', views.delete_record, name='delete'),
]