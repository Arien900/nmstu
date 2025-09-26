from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.index, name='index'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('settings/', views.user_settings, name='user_settings'),
    path('toggle_favorite/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),
]