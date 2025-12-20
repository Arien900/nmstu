from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('presets/', views.presets_view, name='presets'),
    path('presets/use/<int:pid>/', views.use_preset_view, name='use_preset'),
    path('build/create/', views.create_build, name='create_build'),
    path('build/<int:bid>/', views.build_detail, name='build'),
    path('export/', views.export_data, name='export'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('build/<int:build_id>/delete/', views.delete_build_view, name='delete_build'),
    path('build/<int:bid>/edit/', views.edit_build, name='edit_build'),
    path('admin/add-component/', views.admin_add_component, name='admin_add_component'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/export/', views.admin_export_xlsx, name='admin_export_xlsx'),
]