from django.db import models
from django.contrib.auth.models import User
# from django.db.models.signals import post_save
# from django.dispatch import receiver
import uuid

class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.user.username

# Comentamos los signals por ahora para evitar problemas
# @receiver(post_save, sender=User)
# def create_usuario_profile(sender, instance, created, **kwargs):
#     if created:
#         # Usar get_or_create para evitar duplicados
#         Usuario.objects.get_or_create(user=instance)

# @receiver(post_save, sender=User)
# def save_usuario_profile(sender, instance, **kwargs):
#     # Solo guardar si ya existe el perfil
#     try:
#         if hasattr(instance, 'usuario'):
#             instance.usuario.save()
#     except Usuario.DoesNotExist:
#         # Si no existe el perfil, crearlo
#         Usuario.objects.get_or_create(user=instance)

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    # imagen = models.ImageField(upload_to='categorias/', blank=True, null=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    en_venta = models.BooleanField(default=True)  # True = en venta, False = de baja
    # imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    # Stock Keeping Unit
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    destacado = models.BooleanField(default=False)
    descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Porcentaje de descuento")

    def __str__(self):
        return self.nombre

    @property
    def precio_final(self):
        if self.descuento:
            return round(self.precio * (1 - self.descuento / 100), 2)
        return self.precio

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class Pago(models.Model):
    METODO_PAGO_CHOICES = [
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('transferencia', 'Transferencia Bancaria'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comprador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pagos', null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    iva = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    productos_json = models.JSONField()  # Almacenar detalles de productos comprados
    numero_voucher = models.CharField(max_length=20, unique=True)

    def __str__(self):
        comprador_nombre = self.comprador.username if self.comprador else "Cliente invitado"
        return f"Pago {self.numero_voucher} - {comprador_nombre} - ${self.total}"

    class Meta:
        ordering = ['-fecha']

# ===== SISTEMA DE INVENTARIO AVANZADO =====

class Proveedor(models.Model):
    """Modelo para gestionar proveedores"""
    nombre = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, unique=True, help_text="RUT del proveedor (ej: 12345678-9)")
    email = models.EmailField()
    telefono = models.CharField(max_length=15)
    direccion = models.TextField()
    contacto_principal = models.CharField(max_length=100, help_text="Nombre del contacto principal")
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Información financiera
    condicion_pago = models.CharField(max_length=50, default="30 días", help_text="Condición de pago acordada")
    descuento_proveedor = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Descuento por volumen")
    
    def __str__(self):
        return f"{self.nombre} ({self.rut})"
    
    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']

class Ubicacion(models.Model):
    """Modelo para gestionar ubicaciones de almacén"""
    TIPO_UBICACION_CHOICES = [
        ('bodega', 'Bodega Principal'),
        ('salon', 'Salón de Ventas'),
        ('deposito', 'Depósito'),
        ('transito', 'En Tránsito'),
    ]
    
    codigo = models.CharField(max_length=20, unique=True, help_text="Código único (ej: BOD-A1-001)")
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_UBICACION_CHOICES)
    descripcion = models.TextField(blank=True, null=True)
    activa = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    class Meta:
        verbose_name = "Ubicación"
        verbose_name_plural = "Ubicaciones"
        ordering = ['codigo']

class LoteInventario(models.Model):
    """Modelo para gestionar lotes de productos"""
    numero_lote = models.CharField(max_length=50, unique=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='lotes')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='lotes')
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, related_name='lotes')
    
    # Información del lote
    cantidad_inicial = models.PositiveIntegerField()
    cantidad_actual = models.PositiveIntegerField()
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateField(null=True, blank=True, help_text="Fecha de vencimiento si aplica")
    
    # Costos
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, help_text="Costo unitario de compra")
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, help_text="Costo total del lote")
    
    # Estados
    activo = models.BooleanField(default=True)
    reservado = models.PositiveIntegerField(default=0, help_text="Cantidad reservada para ventas")
    
    def __str__(self):
        return f"Lote {self.numero_lote} - {self.producto.nombre}"
    
    @property
    def cantidad_disponible(self):
        return self.cantidad_actual - self.reservado
    
    @property
    def valor_inventario(self):
        return self.cantidad_actual * self.costo_unitario
    
    class Meta:
        verbose_name = "Lote de Inventario"
        verbose_name_plural = "Lotes de Inventario"
        ordering = ['-fecha_ingreso']

class MovimientoInventario(models.Model):
    """Modelo para rastrear todos los movimientos de inventario"""
    TIPO_MOVIMIENTO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('transferencia', 'Transferencia'),
        ('ajuste', 'Ajuste'),
        ('reserva', 'Reserva'),
        ('liberacion', 'Liberación de Reserva'),
    ]
    
    MOTIVO_CHOICES = [
        ('compra', 'Compra a Proveedor'),
        ('venta', 'Venta a Cliente'),
        ('devolucion', 'Devolución'),
        ('merma', 'Merma/Pérdida'),
        ('robo', 'Robo/Faltante'),
        ('transferencia', 'Transferencia entre Ubicaciones'),
        ('ajuste_inventario', 'Ajuste de Inventario'),
        ('reserva_venta', 'Reserva para Venta'),
        ('liberacion_reserva', 'Liberación de Reserva'),
    ]
    
    # Información básica
    fecha = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO_CHOICES)
    motivo = models.CharField(max_length=30, choices=MOTIVO_CHOICES)
    
    # Producto y lote
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    lote = models.ForeignKey(LoteInventario, on_delete=models.CASCADE, related_name='movimientos', null=True, blank=True)
    
    # Ubicaciones
    ubicacion_origen = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, related_name='movimientos_salida', null=True, blank=True)
    ubicacion_destino = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, related_name='movimientos_entrada', null=True, blank=True)
    
    # Cantidades
    cantidad = models.PositiveIntegerField()
    stock_anterior = models.PositiveIntegerField(help_text="Stock antes del movimiento")
    stock_nuevo = models.PositiveIntegerField(help_text="Stock después del movimiento")
    
    # Información adicional
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movimientos_inventario')
    observaciones = models.TextField(blank=True, null=True)
    documento_referencia = models.CharField(max_length=100, blank=True, null=True, help_text="Número de factura, orden, etc.")
    
    def __str__(self):
        return f"{self.tipo.title()} - {self.producto.nombre} - {self.cantidad} unidades"
    
    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = ['-fecha']

class AlertaInventario(models.Model):
    """Modelo para gestionar alertas de inventario"""
    TIPO_ALERTA_CHOICES = [
        ('stock_bajo', 'Stock Bajo'),
        ('stock_critico', 'Stock Crítico'),
        ('sobre_stock', 'Sobre Stock'),
        ('producto_vencido', 'Producto Vencido'),
        ('producto_por_vencer', 'Producto Por Vencer'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('resuelto', 'Resuelto'),
        ('resuelta', 'Resuelta'),  # Alias para compatibilidad
        ('ignorado', 'Ignorado'),
    ]
    
    NIVEL_CHOICES = [
        ('BAJO', 'Bajo'),
        ('MEDIO', 'Medio'),
        ('CRITICO', 'Crítico'),
    ]
    
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='alertas')
    tipo = models.CharField(max_length=20, choices=TIPO_ALERTA_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    nivel = models.CharField(max_length=10, choices=NIVEL_CHOICES, default='MEDIO')
    
    # Información de la alerta
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    stock_actual = models.PositiveIntegerField()
    stock_minimo = models.PositiveIntegerField(null=True, blank=True)
    stock_maximo = models.PositiveIntegerField(null=True, blank=True)
    
    # Responsable
    asignado_a = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alertas_asignadas', null=True, blank=True)
    resuelto_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alertas_resueltas', null=True, blank=True)
    
    mensaje = models.TextField(help_text="Mensaje de la alerta")
    observaciones = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.producto.nombre}"
    
    class Meta:
        verbose_name = "Alerta de Inventario"
        verbose_name_plural = "Alertas de Inventario"
        ordering = ['-fecha_creacion']

class ConfiguracionInventario(models.Model):
    """Modelo para configurar parámetros de inventario por producto"""
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE, related_name='configuracion_inventario')
    
    # Niveles de stock
    stock_minimo = models.PositiveIntegerField(default=10, help_text="Nivel mínimo de stock")
    stock_critico = models.PositiveIntegerField(default=5, help_text="Nivel crítico de stock")
    stock_maximo = models.PositiveIntegerField(default=100, help_text="Nivel máximo de stock")
    punto_reorden = models.PositiveIntegerField(default=20, help_text="Punto de reorden automático")
    
    # Configuración de alertas
    alertas_activas = models.BooleanField(default=True)
    dias_aviso_vencimiento = models.PositiveIntegerField(default=30, help_text="Días de aviso antes del vencimiento")
    
    # Información adicional
    es_critico = models.BooleanField(default=False, help_text="Producto crítico para el negocio")
    rotacion_abc = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C')], default='C', help_text="Clasificación ABC")
    
    def __str__(self):
        return f"Config - {self.producto.nombre}"
    
    class Meta:
        verbose_name = "Configuración de Inventario"
        verbose_name_plural = "Configuraciones de Inventario"
