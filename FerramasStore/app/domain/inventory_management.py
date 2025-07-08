# inventory_management.py - Sistema de Inventario Avanzado

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from decimal import Decimal
import uuid

class InventoryTransaction(models.Model):
    """Registro de transacciones de inventario"""
    TRANSACTION_TYPES = [
        ('in', 'Entrada'),
        ('out', 'Salida'),
        ('adjustment', 'Ajuste'),
        ('return', 'Devolución'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()
    reason = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class StockAlert(models.Model):
    """Alertas de stock bajo"""
    producto = models.OneToOneField('Producto', on_delete=models.CASCADE)
    minimum_threshold = models.IntegerField(default=10)
    reorder_quantity = models.IntegerField(default=50)
    is_active = models.BooleanField(default=True)
    last_alert_sent = models.DateTimeField(null=True, blank=True)
    
    def should_alert(self):
        return self.producto.stock <= self.minimum_threshold

class ProductReview(models.Model):
    """Sistema de reseñas de productos"""
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified_purchase = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['producto', 'user']

class Wishlist(models.Model):
    """Lista de deseos"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'producto']

# Agregar campos al modelo Producto existente
class ProductoExtended(models.Model):
    """Extensión del modelo Producto con funcionalidades avanzadas"""
    
    # Campos adicionales recomendados para el modelo Producto:
    """
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    dimensions = models.CharField(max_length=100, null=True, blank=True)  # "LxWxH"
    barcode = models.CharField(max_length=100, unique=True, null=True, blank=True)
    supplier = models.CharField(max_length=100, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    margin_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=30)
    is_digital = models.BooleanField(default=False)
    requires_shipping = models.BooleanField(default=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=19)  # IVA Chile
    seo_title = models.CharField(max_length=200, null=True, blank=True)
    seo_description = models.TextField(null=True, blank=True)
    """
    
    class Meta:
        abstract = True

# Services para gestión de inventario
class InventoryService:
    """Servicio para gestión de inventario"""
    
    @staticmethod
    def update_stock(producto_id, quantity, transaction_type, reason, user=None):
        """Actualiza stock con registro de transacción"""
        from app.domain.models import Producto
        
        try:
            producto = Producto.objects.get(id=producto_id)
            previous_stock = producto.stock
            
            if transaction_type == 'out' and producto.stock < quantity:
                raise ValidationError(f"Stock insuficiente. Disponible: {producto.stock}")
            
            if transaction_type == 'in':
                producto.stock += quantity
            elif transaction_type == 'out':
                producto.stock -= quantity
            else:  # adjustment
                producto.stock = quantity
            
            producto.save()
            
            # Crear registro de transacción
            InventoryTransaction.objects.create(
                producto=producto,
                transaction_type=transaction_type,
                quantity=quantity,
                previous_stock=previous_stock,
                new_stock=producto.stock,
                reason=reason,
                created_by=user
            )
            
            # Verificar alertas de stock
            InventoryService.check_stock_alerts(producto)
            
            return True
        except Exception as e:
            raise ValidationError(f"Error actualizando stock: {str(e)}")
    
    @staticmethod
    def check_stock_alerts(producto):
        """Verifica y envía alertas de stock bajo"""
        try:
            alert = StockAlert.objects.get(producto=producto)
            if alert.should_alert():
                # Aquí integrarías sistema de notificaciones
                # Por ejemplo: enviar email, notificación push, etc.
                pass
        except StockAlert.DoesNotExist:
            pass

class ProductAnalytics:
    """Análisis de productos"""
    
    @staticmethod
    def get_top_products(limit=10):
        """Productos más vendidos"""
        # Esta función requeriría un modelo de OrderItem
        pass
    
    @staticmethod
    def get_low_stock_products():
        """Productos con stock bajo"""
        from app.domain.models import Producto
        
        alerts = StockAlert.objects.filter(is_active=True)
        low_stock_products = []
        
        for alert in alerts:
            if alert.should_alert():
                low_stock_products.append(alert.producto)
        
        return low_stock_products
