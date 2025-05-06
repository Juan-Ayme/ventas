# core/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet, VentaViewSet

# Crear un router y registrar nuestros viewsets
router = DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'ventas', VentaViewSet)

# Las URLs de la API son determinadas automáticamente por el router
urlpatterns = [
    path('', include(router.urls)),
]
