# models.py

from django.db import models
from django.utils import timezone

class Producto(models.Model):
    """
    Modelo para representar productos en el inventario.
    Campos:
    - nombre: Nombre del producto
    - precio: Precio unitario del producto
    - cantidad_stock: Cantidad disponible en inventario
    """
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_stock = models.IntegerField()

    class Meta:
        # Asegurar que este modelo se vincula con la tabla Productos existente
        db_table = 'Productos'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return f"{self.nombre} - Stock: {self.cantidad_stock}"


class Venta(models.Model):
    """
    Modelo para representar ventas de productos.
    Campos:
    - producto: Relación con el producto vendido
    - cantidad_vendida: Cantidad vendida del producto
    - fecha_venta: Fecha y hora de la venta
    """
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, db_column='ID_Producto')
    cantidad_vendida = models.IntegerField()
    fecha_venta = models.DateTimeField(default=timezone.now)

    class Meta:
        # Asegurar que este modelo se vincula con la tabla Ventas existente
        db_table = 'Ventas'
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'

    def __str__(self):
        return f"Venta de {self.cantidad_vendida} unidades de {self.producto.nombre}"
