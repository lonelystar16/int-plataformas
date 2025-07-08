# 🔐 MEJORAS DE SEGURIDAD PARA FERRAMASSTORE

## 1. CONFIGURACIONES CRÍTICAS EN SETTINGS.PY

### Variables de Entorno
```python
# .env
SECRET_KEY=tu-clave-secreta-super-segura-aqui
DEBUG=False
DB_NAME=ferramas_prod
ALLOWED_HOSTS=tu-dominio.com,localhost
CORS_ALLOWED_ORIGINS=https://tu-dominio.com

# settings.py
import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
```

### Headers de Seguridad
```python
# Agregar a settings.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Para HTTPS en producción
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## 2. RATE LIMITING Y PROTECCIÓN DDOS

### Instalación
```bash
pip install django-ratelimit
```

### Implementación
```python
# views.py
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST')
def login_view(request):
    # Limitar intentos de login
    
@ratelimit(key='ip', rate='3/m', method='POST') 
def register(request):
    # Limitar registro de usuarios
```

## 3. VALIDACIÓN DE ENTRADA MEJORADA

### Formularios Django
```python
# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator

class CustomUserCreationForm(UserCreationForm):
    telefono = forms.CharField(
        validators=[RegexValidator(r'^\+?1?\d{8,15}$', 'Número inválido')]
    )
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email ya registrado")
        return email
```

## 4. AUTENTICACIÓN AVANZADA

### Two-Factor Authentication
```python
# Instalar: pip install django-otp

INSTALLED_APPS += ['django_otp']
MIDDLEWARE += ['django_otp.middleware.OTPMiddleware']
```

### Bloqueo de Cuenta
```python
# models.py
class UserLoginAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    attempted_at = models.DateTimeField(auto_now_add=True)
    successful = models.BooleanField(default=False)
```

## 5. PROTECCIÓN CSRF MEJORADA

### Rotación de Tokens
```python
# settings.py
CSRF_COOKIE_AGE = 7200  # 2 horas
CSRF_TOKEN_TTLS = 3600   # 1 hora

# middleware personalizado
class CSRFRotationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.method == 'POST':
            # Rotar token después de operaciones críticas
            csrf.rotate_token(request)
        return response
```
