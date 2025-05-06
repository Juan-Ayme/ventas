# sistema/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, F
from django.utils import timezone
from datetime import timedelta

from .models import Producto, Venta
from .serializers import (
    ProductoSerializer,
    VentaSerializer,
    VentaDetalladaSerializer,
    CrearVentaSerializer
)


class ProductoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para ver y editar productos.

    Proporciona operaciones CRUD:
    - list (GET): listar todos los productos
    - retrieve (GET): obtener un producto por ID
    - create (POST): crear un nuevo producto
    - update (PUT): actualizar un producto existente
    - partial_update (PATCH): actualizar parcialmente un producto
    - destroy (DELETE): eliminar un producto
    """
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    @action(detail=False, methods=['get'])
    def agotados(self, request):
        """
        Endpoint adicional para obtener productos agotados o con bajo stock.
        GET /api/productos/agotados/
        """
        productos_agotados = Producto.objects.filter(cantidad_stock__lte=5)
        serializer = self.get_serializer(productos_agotados, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Sobrescribir el método destroy para impedir la eliminación de productos con ventas asociadas.
        """
        producto = self.get_object()
        # Verificar si hay ventas asociadas a este producto
        if Venta.objects.filter(producto=producto).exists():
            return Response(
                {"error": "No se puede eliminar este producto porque tiene ventas asociadas."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


class VentaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para ver y editar ventas.

    Proporciona operaciones CRUD:
    - list (GET): listar todas las ventas
    - retrieve (GET): obtener una venta por ID
    - create (POST): crear una nueva venta
    - update (PUT): actualizar una venta existente
    - partial_update (PATCH): actualizar parcialmente una venta
    - destroy (DELETE): eliminar una venta
    """
    queryset = Venta.objects.all()

    def get_serializer_class(self):
        """
        Usar diferentes serializadores dependiendo de la acción:
        - Para crear: usar CrearVentaSerializer con validación de stock
        - Para listar/recuperar: usar VentaDetalladaSerializer con información del producto
        - Para otras acciones: usar VentaSerializer básico
        """
        if self.action == 'create':
            return CrearVentaSerializer
        elif self.action in ['list', 'retrieve']:
            return VentaDetalladaSerializer
        return VentaSerializer

    @action(detail=False, methods=['get'])
    def reporte_diario(self, request):
        """
        Endpoint adicional para obtener un reporte de ventas del día actual.
        GET /api/ventas/reporte_diario/
        """
        hoy = timezone.now().date()
        ventas_hoy = Venta.objects.filter(
            fecha_venta__date=hoy
        ).select_related('producto')

        # Calcular total de ventas
        total_ventas = ventas_hoy.count()

        # Calcular ingresos totales
        ingresos = 0
        for venta in ventas_hoy:
            ingresos += venta.producto.precio * venta.cantidad_vendida

        # Productos más vendidos
        productos_vendidos = (
            ventas_hoy.values('producto__nombre')
            .annotate(
                total_vendido=Sum('cantidad_vendida'),
                producto_nombre=F('producto__nombre')
            )
            .order_by('-total_vendido')[:5]
        )

        return Response({
            'fecha': hoy,
            'total_ventas': total_ventas,
            'ingresos_totales': ingresos,
            'productos_mas_vendidos': productos_vendidos
        })

    @action(detail=False, methods=['get'])
    def ultimas_ventas(self, request):
        """
        Endpoint adicional para obtener las últimas ventas realizadas.
        GET /api/ventas/ultimas_ventas/
        """
        # Obtener las últimas 10 ventas
        ultimas_ventas = Venta.objects.all().order_by('-fecha_venta')[:10]
        serializer = VentaDetalladaSerializer(ultimas_ventas, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Sobrescribir el método destroy para restaurar el stock al eliminar una venta.
        """
        venta = self.get_object()
        producto = venta.producto

        # Restaurar stock del producto
        producto.cantidad_stock += venta.cantidad_vendida
        producto.save()

        return super().destroy(request, *args, **kwargs)
