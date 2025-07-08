# notification_system.py - Sistema de Notificaciones

from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import uuid
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class NotificationType(models.Model):
    """Tipos de notificaciones"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    template_email = models.CharField(max_length=200, null=True, blank=True)
    template_sms = models.CharField(max_length=200, null=True, blank=True)
    is_active = models.BooleanField(default=True)

class Notification(models.Model):
    """Notificaciones del sistema"""
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('normal', 'Normal'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('sent', 'Enviada'),
        ('delivered', 'Entregada'),
        ('failed', 'Fallida'),
        ('read', 'Leída'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    recipient_email = models.EmailField(null=True, blank=True)  # Para invitados
    
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Configuración de envío
    send_email = models.BooleanField(default=True)
    send_sms = models.BooleanField(default=False)
    send_push = models.BooleanField(default=True)
    send_in_app = models.BooleanField(default=True)
    
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Metadatos
    data = models.JSONField(default=dict, blank=True)  # Datos adicionales
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)  # Para notificaciones programadas
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Configuración de reintento
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['status', 'scheduled_at']),
        ]

class UserNotificationPreference(models.Model):
    """Preferencias de notificación por usuario"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Preferencias por tipo
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    
    # Frecuencia
    digest_frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Inmediato'),
            ('daily', 'Diario'),
            ('weekly', 'Semanal'),
            ('never', 'Nunca'),
        ],
        default='immediate'
    )
    
    # Tipos específicos
    order_updates = models.BooleanField(default=True)
    marketing = models.BooleanField(default=True)
    security_alerts = models.BooleanField(default=True)
    stock_alerts = models.BooleanField(default=False)
    
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)

class EmailTemplate(models.Model):
    """Plantillas de email"""
    name = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=200)
    html_content = models.TextField()
    text_content = models.TextField()
    variables = models.JSONField(default=list)  # Variables disponibles
    is_active = models.BooleanField(default=True)

# Services
class NotificationService:
    """Servicio de notificaciones"""
    
    @staticmethod
    def send_notification(
        recipient=None, 
        recipient_email=None,
        notification_type='general',
        title='',
        message='',
        data=None,
        priority='normal',
        send_email=True,
        send_push=True
    ):
        """Envía una notificación"""
        try:
            # Obtener o crear tipo de notificación
            notif_type, created = NotificationType.objects.get_or_create(
                name=notification_type,
                defaults={'description': notification_type.replace('_', ' ').title()}
            )
            
            # Crear notificación
            notification = Notification.objects.create(
                recipient=recipient,
                recipient_email=recipient_email or (recipient.email if recipient else None),
                notification_type=notif_type,
                title=title,
                message=message,
                data=data or {},
                priority=priority,
                send_email=send_email,
                send_push=send_push
            )
            
            # Procesar envío
            NotificationService._process_notification(notification)
            
            return notification
            
        except Exception as e:
            print(f"Error enviando notificación: {e}")
            return None
    
    @staticmethod
    def _process_notification(notification):
        """Procesa y envía la notificación"""
        try:
            # Email
            if notification.send_email and notification.recipient_email:
                NotificationService._send_email(notification)
            
            # Push notification (WebSocket)
            if notification.send_push and notification.recipient:
                NotificationService._send_push(notification)
            
            # In-app notification (ya se guarda en BD)
            
            notification.status = 'sent'
            notification.save()
            
        except Exception as e:
            notification.status = 'failed'
            notification.retry_count += 1
            notification.save()
            print(f"Error procesando notificación: {e}")
    
    @staticmethod
    def _send_email(notification):
        """Envía email"""
        try:
            context = {
                'title': notification.title,
                'message': notification.message,
                'data': notification.data,
                'user': notification.recipient
            }
            
            # Usar plantilla si existe
            template_name = f'emails/{notification.notification_type.name}.html'
            
            send_mail(
                subject=notification.title,
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.recipient_email],
                html_message=render_to_string(template_name, context) if notification.notification_type.template_email else None
            )
            
        except Exception as e:
            print(f"Error enviando email: {e}")
            raise
    
    @staticmethod
    def _send_push(notification):
        """Envía notificación push vía WebSocket"""
        try:
            if not notification.recipient:
                return
            
            channel_layer = get_channel_layer()
            group_name = f"user_{notification.recipient.id}"
            
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'notification_message',
                    'message': {
                        'id': str(notification.id),
                        'title': notification.title,
                        'message': notification.message,
                        'priority': notification.priority,
                        'data': notification.data,
                        'created_at': notification.created_at.isoformat()
                    }
                }
            )
            
        except Exception as e:
            print(f"Error enviando push: {e}")
    
    @staticmethod
    def send_order_notification(order, status_change=None):
        """Notificaciones específicas de órdenes"""
        templates = {
            'pending': {
                'title': f'Orden #{order.order_number} recibida',
                'message': 'Hemos recibido tu orden y la estamos procesando.'
            },
            'confirmed': {
                'title': f'Orden #{order.order_number} confirmada',
                'message': 'Tu orden ha sido confirmada y será procesada pronto.'
            },
            'shipped': {
                'title': f'Orden #{order.order_number} enviada',
                'message': f'Tu orden ha sido enviada. Tracking: {order.tracking_number}'
            },
            'delivered': {
                'title': f'Orden #{order.order_number} entregada',
                'message': '¡Tu orden ha sido entregada! ¿Qué tal fue tu experiencia?'
            }
        }
        
        if status_change and status_change in templates:
            template = templates[status_change]
            
            NotificationService.send_notification(
                recipient=order.user,
                recipient_email=order.guest_email if not order.user else None,
                notification_type='order_update',
                title=template['title'],
                message=template['message'],
                data={
                    'order_id': str(order.id),
                    'order_number': order.order_number,
                    'status': status_change,
                    'tracking_number': order.tracking_number
                },
                priority='high'
            )
    
    @staticmethod
    def send_stock_alert(producto):
        """Alerta de stock bajo para administradores"""
        from django.contrib.auth.models import User
        
        admins = User.objects.filter(is_staff=True)
        
        for admin in admins:
            NotificationService.send_notification(
                recipient=admin,
                notification_type='stock_alert',
                title=f'Stock bajo: {producto.nombre}',
                message=f'El producto {producto.nombre} tiene stock bajo ({producto.stock} unidades).',
                data={
                    'producto_id': producto.id,
                    'stock_actual': producto.stock,
                    'sku': producto.sku
                },
                priority='high'
            )

# WebSocket Consumer para notificaciones en tiempo real
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    """Consumer para notificaciones en tiempo real"""
    
    async def connect(self):
        if self.scope["user"].is_authenticated:
            self.group_name = f"user_{self.scope['user'].id}"
            
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            
            await self.accept()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def notification_message(self, event):
        """Envía notificación al cliente"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'data': event['message']
        }))
