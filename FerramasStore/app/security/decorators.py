# FerramasStore/app/security/decorators.py
import logging
from functools import wraps
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone
from django.core.cache import cache
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
from django.conf import settings

logger = logging.getLogger('security')

def secure_auth_view(rate='5/5m', block=False):
    """
    Decorador para vistas de autenticación con rate limiting y logging de seguridad
    """
    def decorator(view_func):
        @wraps(view_func)
        @ratelimit(key='ip', rate=rate, block=block)
        def wrapper(request, *args, **kwargs):
            try:
                # Verificar si fue rate limited
                if getattr(request, 'limited', False):
                    logger.error(f"Rate limit excedido para IP {request.META.get('REMOTE_ADDR')} en vista {view_func.__name__}")
                    
                    if request.is_ajax() or request.content_type == 'application/json':
                        return JsonResponse({
                            'error': 'Demasiados intentos. Inténtalo más tarde.',
                            'retry_after': 300
                        }, status=429)
                    else:
                        messages.error(request, 'Demasiados intentos de login. Por favor espera 5 minutos antes de intentar nuevamente.')
                        return render(request, 'pages/rate_limit_exceeded.html', {
                            'retry_after': 300,
                            'attempts_made': 5,
                            'wait_time': '5 minutos',
                            'debug': settings.DEBUG
                        })
                
                # Logging de intentos de acceso
                if request.method == 'POST':
                    username = request.POST.get('usuario', 'unknown')
                    logger.warning(f"Intento de login desde IP {request.META.get('REMOTE_ADDR')} para usuario {username}")
                
                return view_func(request, *args, **kwargs)
                
            except Exception as e:
                logger.error(f"Error en vista segura {view_func.__name__}: {str(e)}")
                messages.error(request, 'Error interno del servidor. Inténtalo más tarde.')
                return redirect('app:login')
                    
        return wrapper
    return decorator

def track_failed_login(username, ip_address):
    """
    Rastrea intentos fallidos de login
    """
    key = f"failed_login_{ip_address}_{username}"
    current_count = cache.get(key, 0)
    cache.set(key, current_count + 1, 300)  # 5 minutos
    
    if current_count >= settings.LOGIN_ATTEMPTS_LIMIT:
        logger.error(f"Usuario {username} bloqueado temporalmente desde IP {ip_address}")
        return True
    return False

def is_login_blocked(username, ip_address):
    """
    Verifica si el login está bloqueado para un usuario/IP
    """
    key = f"failed_login_{ip_address}_{username}"
    count = cache.get(key, 0)
    return count >= settings.LOGIN_ATTEMPTS_LIMIT

def clear_failed_login_attempts(username, ip_address):
    """
    Limpia los intentos fallidos después de un login exitoso
    """
    key = f"failed_login_{ip_address}_{username}"
    cache.delete(key)

def honeypot_check(view_func):
    """
    Decorador para detectar bots usando campos honeypot
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.method == 'POST':
            # Campo honeypot que debe estar vacío
            honeypot_value = request.POST.get('website', '')
            if honeypot_value:
                logger.warning(f"Bot detectado desde IP {request.META.get('REMOTE_ADDR')} - honeypot field filled")
                return JsonResponse({'error': 'Invalid request'}, status=400)
        
        return view_func(request, *args, **kwargs)
    return wrapper

def log_suspicious_activity(request, activity_type, details=""):
    """
    Función para logging de actividades sospechosas
    """
    logger.warning(f"Actividad sospechosa: {activity_type} desde IP {request.META.get('REMOTE_ADDR')} - {details}")

def secure_api_view(rate='100/h'):
    """
    Decorador para endpoints API con rate limiting
    """
    def decorator(view_func):
        @wraps(view_func)
        @ratelimit(key='ip', rate=rate, block=True)
        def wrapper(request, *args, **kwargs):
            try:
                return view_func(request, *args, **kwargs)
            except Ratelimited:
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'message': 'Too many requests. Please try again later.'
                }, status=429)
        return wrapper
    return decorator
