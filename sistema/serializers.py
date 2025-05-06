# sistema/serializers.py

from rest_framework import serializers
from .models import Producto, Venta


class ProductoSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Producto.
    Convierte objetos Producto a JSON y viceversa.
    """
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'precio', 'cantidad_stock']


class VentaSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Venta.
    Convierte objetos Venta a JSON y viceversa.
    """
    class Meta:
        model = Venta
        fields = ['id', 'producto', 'cantidad_vendida', 'fecha_venta']


class VentaDetalladaSerializer(serializers.ModelSerializer):
    """
    Serializador para mostrar detalles adicionales de una venta,
    incluyendo información del producto.
    """
    producto = ProductoSerializer(read_only=True)

    class Meta:
        model = Venta
        fields = ['id', 'producto', 'cantidad_vendida', 'fecha_venta']


class CrearVentaSerializer(serializers.ModelSerializer):
    """
    Serializador específico para crear ventas con validación adicional
    para verificar el stock disponible.
    """
    class Meta:
        model = Venta
        fields = ['producto', 'cantidad_vendida']

    def validate(self, data):
        """
        Validar que la cantidad vendida no exceda el stock disponible.
        """
        producto = data['producto']
        cantidad_vendida = data['cantidad_vendida']

        if cantidad_vendida <= 0:
            raise serializers.ValidationError("La cantidad vendida debe ser mayor que cero.")

        if cantidad_vendida > producto.cantidad_stock:
            raise serializers.ValidationError(
                f"Stock insuficiente. Solo hay {producto.cantidad_stock} unidades disponibles."
            )

        return data

    def create(self, validated_data):
        """
        Crear una venta y actualizar el stock del producto.
        """
        producto = validated_data['producto']
        cantidad_vendida = validated_data['cantidad_vendida']

        # Actualizar el stock
        producto.cantidad_stock -= cantidad_vendida
        producto.save()

        # Crear la venta
        venta = Venta.objects.create(**validated_data)
        return venta
