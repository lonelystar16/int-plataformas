# analytics_system.py - Sistema de Analytics

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import json
from datetime import datetime, timedelta

class AnalyticsEvent(models.Model):
    """Eventos de analytics"""
    EVENT_TYPES = [
        ('page_view', 'Vista de Página'),
        ('product_view', 'Vista de Producto'),
        ('add_to_cart', 'Agregar al Carrito'),
        ('remove_from_cart', 'Quitar del Carrito'),
        ('purchase', 'Compra'),
        ('search', 'Búsqueda'),
        ('user_registration', 'Registro de Usuario'),
        ('user_login', 'Inicio de Sesión'),
        ('newsletter_signup', 'Suscripción Newsletter'),
    ]
    
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    # Datos específicos del evento
    page_url = models.URLField(null=True, blank=True)
    referrer = models.URLField(null=True, blank=True)
    product_id = models.IntegerField(null=True, blank=True)
    search_query = models.CharField(max_length=200, null=True, blank=True)
    
    # Datos adicionales en JSON
    metadata = models.JSONField(default=dict)
    
    # Información geográfica
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['session_id']),
        ]

class UserSession(models.Model):
    """Sesiones de usuario"""
    session_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Métricas de sesión
    page_views = models.IntegerField(default=0)
    duration_seconds = models.IntegerField(null=True)  # Duración en segundos
    bounce = models.BooleanField(default=True)  # True si solo vio una página
    converted = models.BooleanField(default=False)  # True si hizo una compra
    
    # Información de dispositivo
    device_type = models.CharField(max_length=20, null=True, blank=True)  # mobile, tablet, desktop
    browser = models.CharField(max_length=50, null=True, blank=True)
    os = models.CharField(max_length=50, null=True, blank=True)

class ProductAnalytics(models.Model):
    """Analytics específicos de productos"""
    producto = models.OneToOneField('Producto', on_delete=models.CASCADE)
    
    # Métricas de vista
    total_views = models.IntegerField(default=0)
    unique_views = models.IntegerField(default=0)
    views_last_7_days = models.IntegerField(default=0)
    views_last_30_days = models.IntegerField(default=0)
    
    # Métricas de conversión
    times_added_to_cart = models.IntegerField(default=0)
    times_purchased = models.IntegerField(default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Métricas de búsqueda
    search_appearances = models.IntegerField(default=0)
    search_clicks = models.IntegerField(default=0)
    
    # Datos demográficos
    top_countries = models.JSONField(default=list)
    top_cities = models.JSONField(default=list)
    
    last_updated = models.DateTimeField(auto_now=True)

class SalesReport(models.Model):
    """Reportes de ventas diarios"""
    date = models.DateField(unique=True)
    
    # Métricas de ventas
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_orders = models.IntegerField(default=0)
    total_items_sold = models.IntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Métricas de usuarios
    new_customers = models.IntegerField(default=0)
    returning_customers = models.IntegerField(default=0)
    
    # Métricas de productos
    unique_products_sold = models.IntegerField(default=0)
    top_selling_product_id = models.IntegerField(null=True, blank=True)
    
    # Métricas de tráfico
    total_sessions = models.IntegerField(default=0)
    unique_visitors = models.IntegerField(default=0)
    bounce_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

# Services
class AnalyticsService:
    """Servicio para analytics"""
    
    @staticmethod
    def track_event(event_type, request, **kwargs):
        """Registra un evento de analytics"""
        try:
            # Obtener información de la sesión
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key
            
            # Crear evento
            event = AnalyticsEvent.objects.create(
                event_type=event_type,
                user=request.user if request.user.is_authenticated else None,
                session_id=session_id,
                ip_address=AnalyticsService._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                page_url=request.build_absolute_uri(),
                referrer=request.META.get('HTTP_REFERER', ''),
                **kwargs
            )
            
            # Actualizar sesión
            AnalyticsService._update_session(request, event_type)
            
            # Actualizar métricas de producto si aplica
            if event_type == 'product_view' and 'product_id' in kwargs:
                AnalyticsService._update_product_analytics(kwargs['product_id'], event_type)
            
            return event
            
        except Exception as e:
            print(f"Error tracking event: {e}")
            return None
    
    @staticmethod
    def _get_client_ip(request):
        """Obtiene la IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def _update_session(request, event_type):
        """Actualiza información de la sesión"""
        try:
            session_id = request.session.session_key
            user_session, created = UserSession.objects.get_or_create(
                session_id=session_id,
                defaults={
                    'user': request.user if request.user.is_authenticated else None,
                    'ip_address': AnalyticsService._get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                }
            )
            
            # Actualizar actividad
            session.last_activity = timezone.now()
            
            # Incrementar vistas de página
            if event_type == 'page_view':
                user_session.page_views += 1
                if user_session.page_views > 1:
                    user_session.bounce = False
            
            # Marcar como convertido si hizo una compra
            if event_type == 'purchase':
                user_session.converted = True
            
            user_session.save()
            
        except Exception as e:
            print(f"Error updating session: {e}")
    
    @staticmethod
    def _update_product_analytics(product_id, event_type):
        """Actualiza analytics del producto"""
        try:
            from app.domain.models import Producto
            producto = Producto.objects.get(id=product_id)
            analytics, created = ProductAnalytics.objects.get_or_create(
                producto=producto
            )
            
            if event_type == 'product_view':
                analytics.total_views += 1
                # Actualizar vistas por período (esto se puede hacer con tareas periódicas)
                
            elif event_type == 'add_to_cart':
                analytics.times_added_to_cart += 1
                
            elif event_type == 'purchase':
                analytics.times_purchased += 1
            
            # Calcular tasa de conversión
            if analytics.total_views > 0:
                analytics.conversion_rate = (analytics.times_purchased / analytics.total_views) * 100
            
            analytics.save()
            
        except Exception as e:
            print(f"Error updating product analytics: {e}")
    
    @staticmethod
    def generate_daily_report(date=None):
        """Genera reporte diario"""
        if date is None:
            date = timezone.now().date()
        
        try:
            # Obtener datos del día
            start_date = datetime.combine(date, datetime.min.time())
            end_date = start_date + timedelta(days=1)
            
            # Métricas de ventas (requiere modelo Order)
            # sales_data = Order.objects.filter(
            #     created_at__gte=start_date,
            #     created_at__lt=end_date,
            #     status__in=['completed', 'delivered']
            # ).aggregate(
            #     total_sales=models.Sum('total'),
            #     total_orders=models.Count('id'),
            #     avg_order_value=models.Avg('total')
            # )
            
            # Métricas de tráfico
            sessions = UserSession.objects.filter(
                started_at__gte=start_date,
                started_at__lt=end_date
            )
            
            total_sessions = sessions.count()
            unique_visitors = sessions.values('ip_address').distinct().count()
            bounce_sessions = sessions.filter(bounce=True).count()
            bounce_rate = (bounce_sessions / total_sessions * 100) if total_sessions > 0 else 0
            
            # Crear o actualizar reporte
            report, created = SalesReport.objects.update_or_create(
                date=date,
                defaults={
                    'total_sessions': total_sessions,
                    'unique_visitors': unique_visitors,
                    'bounce_rate': bounce_rate,
                    # 'total_sales': sales_data['total_sales'] or 0,
                    # 'total_orders': sales_data['total_orders'] or 0,
                    # 'average_order_value': sales_data['avg_order_value'] or 0,
                }
            )
            
            return report
            
        except Exception as e:
            print(f"Error generating daily report: {e}")
            return None
    
    @staticmethod
    def get_dashboard_stats(days=30):
        """Obtiene estadísticas para el dashboard"""
        try:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            # Estadísticas generales
            stats = {
                'total_page_views': AnalyticsEvent.objects.filter(
                    event_type='page_view',
                    created_at__gte=start_date
                ).count(),
                
                'unique_visitors': AnalyticsEvent.objects.filter(
                    created_at__gte=start_date
                ).values('session_id').distinct().count(),
                
                'bounce_rate': UserSession.objects.filter(
                    started_at__gte=start_date,
                    bounce=True
                ).count(),
                
                'conversion_rate': 0,  # Calcular basado en compras vs visitas
            }
            
            # Top productos
            top_products = ProductAnalytics.objects.select_related('producto').order_by(
                '-views_last_30_days'
            )[:10]
            
            stats['top_products'] = [
                {
                    'name': p.producto.nombre,
                    'views': p.views_last_30_days,
                    'conversion_rate': float(p.conversion_rate)
                }
                for p in top_products
            ]
            
            # Datos para gráficos
            daily_stats = []
            for i in range(days):
                day = start_date.date() + timedelta(days=i)
                day_events = AnalyticsEvent.objects.filter(
                    event_type='page_view',
                    created_at__date=day
                ).count()
                
                daily_stats.append({
                    'date': day.isoformat(),
                    'views': day_events
                })
            
            stats['daily_views'] = daily_stats
            
            return stats
            
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {}

class AnalyticsMiddleware:
    """Middleware para tracking automático"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Procesar antes de la vista
        response = self.get_response(request)
        
        # Tracking automático después de la respuesta
        if response.status_code == 200:
            self.track_page_view(request)
        
        return response
    
    def track_page_view(self, request):
        """Track automático de vistas de página"""
        # Solo trackear GET requests
        if request.method == 'GET':
            # Excluir rutas admin y API
            if not request.path.startswith('/admin/') and not request.path.startswith('/api/'):
                AnalyticsService.track_event('page_view', request)

# Decorador para tracking específico
def track_event(event_type, **event_kwargs):
    """Decorador para tracking de eventos específicos"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            # Ejecutar vista
            response = view_func(request, *args, **kwargs)
            
            # Track evento
            AnalyticsService.track_event(event_type, request, **event_kwargs)
            
            return response
        return wrapper
    return decorator

# Funciones de utilidad para templates
def get_popular_products(limit=5):
    """Obtiene productos populares para mostrar en templates"""
    return ProductAnalytics.objects.select_related('producto').order_by(
        '-views_last_7_days'
    )[:limit]

def get_trending_searches(limit=10):
    """Obtiene búsquedas populares"""
    from django.db.models import Count
    
    recent_searches = AnalyticsEvent.objects.filter(
        event_type='search',
        created_at__gte=timezone.now() - timedelta(days=7)
    ).values('search_query').annotate(
        count=Count('search_query')
    ).order_by('-count')[:limit]
    
    return [s['search_query'] for s in recent_searches if s['search_query']]
