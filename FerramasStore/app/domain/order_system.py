# order_system.py - Sistema de Órdenes Completo

from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
import uuid
from django.utils import timezone

class Order(models.Model):
    """Modelo de Orden de Compra"""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmada'),
        ('processing', 'Procesando'),
        ('shipped', 'Enviada'),
        ('delivered', 'Entregada'),
        ('cancelled', 'Cancelada'),
        ('refunded', 'Reembolsada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Información del cliente (para invitados)
    guest_name = models.CharField(max_length=100, null=True, blank=True)
    guest_email = models.EmailField(null=True, blank=True)
    guest_phone = models.CharField(max_length=20, null=True, blank=True)
    
    # Información de envío
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_region = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=10)
    
    # Información de facturación (puede ser diferente al envío)
    billing_address = models.TextField(null=True, blank=True)
    billing_city = models.CharField(max_length=100, null=True, blank=True)
    billing_region = models.CharField(max_length=100, null=True, blank=True)
    billing_postal_code = models.CharField(max_length=10, null=True, blank=True)
    
    # Totales
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Estado y fechas
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Información adicional
    notes = models.TextField(blank=True)
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """Genera número de orden único"""
        import random
        import string
        timestamp = timezone.now().strftime('%Y%m%d')
        random_part = ''.join(random.choices(string.digits, k=4))
        return f"FER-{timestamp}-{random_part}"

class OrderItem(models.Model):
    """Elementos de la orden"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    
    # Información del producto al momento de la compra
    product_name = models.CharField(max_length=200)  # Snapshot
    product_sku = models.CharField(max_length=50, null=True)
    
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_per_item = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        # Calcular total automáticamente
        self.total_price = (self.unit_price - self.discount_per_item) * self.quantity
        super().save(*args, **kwargs)

class OrderStatusHistory(models.Model):
    """Historial de cambios de estado"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20, null=True)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

class ShippingMethod(models.Model):
    """Métodos de envío"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    estimated_days = models.IntegerField()
    is_active = models.BooleanField(default=True)
    free_shipping_threshold = models.DecimalField(
        max_digits=10, decimal_places=2, 
        null=True, blank=True,
        help_text="Monto mínimo para envío gratis"
    )

class Coupon(models.Model):
    """Sistema de cupones"""
    DISCOUNT_TYPES = [
        ('percentage', 'Porcentaje'),
        ('fixed', 'Monto Fijo'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    minimum_order_amount = models.DecimalField(
        max_digits=10, decimal_places=2, 
        null=True, blank=True
    )
    
    # Límites de uso
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    usage_limit_per_user = models.PositiveIntegerField(null=True, blank=True)
    
    # Fechas de validez
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_valid(self):
        """Verifica si el cupón es válido"""
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_until and
            (self.usage_limit is None or self.used_count < self.usage_limit)
        )

class CouponUsage(models.Model):
    """Registro de uso de cupones"""
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    used_at = models.DateTimeField(auto_now_add=True)

# Services
class OrderService:
    """Servicio para gestión de órdenes"""
    
    @staticmethod
    def create_order_from_cart(cart_data, user=None, guest_info=None, shipping_info=None):
        """Crea una orden desde el carrito"""
        try:
            # Calcular totales
            subtotal = Decimal('0')
            items_data = []
            
            for item in cart_data:
                from app.domain.models import Producto
                producto = Producto.objects.get(id=item['id'])
                
                # Verificar stock
                if producto.stock < item['cantidad']:
                    raise ValueError(f"Stock insuficiente para {producto.nombre}")
                
                item_total = Decimal(str(producto.precio_final)) * item['cantidad']
                subtotal += item_total
                
                items_data.append({
                    'producto': producto,
                    'quantity': item['cantidad'],
                    'unit_price': producto.precio_final,
                    'total_price': item_total
                })
            
            # Aplicar descuentos si está autenticado
            discount = Decimal('0')
            if user and user.is_authenticated:
                discount = subtotal * Decimal('0.10')  # 10% descuento
            
            subtotal_with_discount = subtotal - discount
            tax = subtotal_with_discount * Decimal('0.19')  # IVA Chile
            total = subtotal_with_discount + tax
            
            # Crear orden
            order = Order.objects.create(
                user=user if user and user.is_authenticated else None,
                guest_name=guest_info.get('name') if guest_info else None,
                guest_email=guest_info.get('email') if guest_info else None,
                shipping_address=shipping_info.get('address', ''),
                shipping_city=shipping_info.get('city', ''),
                shipping_region=shipping_info.get('region', ''),
                shipping_postal_code=shipping_info.get('postal_code', ''),
                subtotal=subtotal,
                discount_amount=discount,
                tax_amount=tax,
                total=total
            )
            
            # Crear items de la orden
            for item_data in items_data:
                OrderItem.objects.create(
                    order=order,
                    producto=item_data['producto'],
                    product_name=item_data['producto'].nombre,
                    product_sku=item_data['producto'].sku,
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    total_price=item_data['total_price']
                )
                
                # Actualizar stock
                from app.domain.inventory_management import InventoryService
                InventoryService.update_stock(
                    item_data['producto'].id,
                    item_data['quantity'],
                    'out',
                    f'Venta - Orden {order.order_number}',
                    user
                )
            
            return order
            
        except Exception as e:
            raise ValueError(f"Error creando orden: {str(e)}")
    
    @staticmethod
    def update_order_status(order_id, new_status, user=None, notes=''):
        """Actualiza estado de la orden"""
        try:
            order = Order.objects.get(id=order_id)
            old_status = order.status
            
            order.status = new_status
            
            # Actualizar fechas especiales
            if new_status == 'shipped':
                order.shipped_at = timezone.now()
            elif new_status == 'delivered':
                order.delivered_at = timezone.now()
            
            order.save()
            
            # Crear registro de historial
            OrderStatusHistory.objects.create(
                order=order,
                old_status=old_status,
                new_status=new_status,
                changed_by=user,
                notes=notes
            )
            
            return order
            
        except Exception as e:
            raise ValueError(f"Error actualizando estado: {str(e)}")
