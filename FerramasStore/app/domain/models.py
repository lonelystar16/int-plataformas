from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_usuario_profile(sender, instance, created, **kwargs):
    if created:
        Usuario.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_usuario_profile(sender, instance, **kwargs):
    if hasattr(instance, 'usuario'):
        instance.usuario.save()

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
