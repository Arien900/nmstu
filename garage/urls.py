# garage/urls.py
from rest_framework import routers
from .views import CarViewSet, ServiceViewSet, MechanicViewSet

router = routers.DefaultRouter()
router.register(r'cars', CarViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'mechanics', MechanicViewSet)

urlpatterns = router.urls
