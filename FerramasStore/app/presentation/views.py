# FerramasStore/app/presentation/views.py
from ..domain.models import Producto, Categoria, Usuario
# Django imports
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import logging
# External API services
from app.infrastructure.external_services.api_externa import obtener_valor_dolar, obtener_productos, crear_preferencia_pago
# Security imports
from app.security.decorators import (
    secure_auth_view, track_failed_login, is_login_blocked, 
    clear_failed_login_attempts, honeypot_check, log_suspicious_activity
)
from app.security.validators import (
    validate_chilean_phone, validate_strong_password, 
    validate_email_domain, sanitize_html_input
)

# Configurar loggers
security_logger = logging.getLogger('security')
auth_logger = logging.getLogger('auth')
import logging

# Logger de seguridad
security_logger = logging.getLogger('security')
auth_logger = logging.getLogger('auth')

def index(request):
    return render(request, 'pages/mainPage.html')

def herra_manuales(request):
    try:
        categoria = Categoria.objects.filter(nombre='Herramientas Manuales').first()
        if not categoria:
            return render(request, 'pages/herra-manuales.html', {
                'productos': [],
                'error': 'Categoría "Herramientas Manuales" no encontrada'
            })
        
        productos = Producto.objects.filter(categoria=categoria, en_venta=True)
        return render(request, 'pages/herra-manuales.html', {'productos': productos})
    
    except Exception as e:
        return render(request, 'pages/herra-manuales.html', {
            'productos': [],
            'error': f'Error al cargar productos: {str(e)}'
        })

def materiales_basicos(request):
    try:
        categoria = Categoria.objects.filter(nombre='Materiales Básicos').first()
        if not categoria:
            return render(request, 'pages/materiales-basicos.html', {
                'productos': [],
                'error': 'Categoría "Materiales Básicos" no encontrada'
            })
        
        productos = Producto.objects.filter(categoria=categoria, en_venta=True)
        return render(request, 'pages/materiales-basicos.html', {'productos': productos})
    
    except Exception as e:
        return render(request, 'pages/materiales-basicos.html', {
            'productos': [],
            'error': f'Error al cargar productos: {str(e)}'
        })

def equipos_seguridad(request):
    try:
        categoria = Categoria.objects.filter(nombre='Equipos de Seguridad').first()
        if not categoria:
            return render(request, 'pages/equipos-seguridad.html', {
                'productos': [],
                'error': 'Categoría "Equipos de Seguridad" no encontrada'
            })
        
        productos = Producto.objects.filter(categoria=categoria, en_venta=True)
        return render(request, 'pages/equipos-seguridad.html', {'productos': productos})
    
    except Exception as e:
        return render(request, 'pages/equipos-seguridad.html', {
            'productos': [],
            'error': f'Error al cargar productos: {str(e)}'
        })

def tornillos_anclaje(request):
    try:
        categoria = Categoria.objects.filter(nombre='Tornillos y Anclajes').first()
        if not categoria:
            return render(request, 'pages/tornillos-anclaje.html', {
                'productos': [],
                'error': 'Categoría "Tornillos y Anclajes" no encontrada'
            })
        
        productos = Producto.objects.filter(categoria=categoria, en_venta=True)
        return render(request, 'pages/tornillos-anclaje.html', {'productos': productos})
    
    except Exception as e:
        return render(request, 'pages/tornillos-anclaje.html', {
            'productos': [],
            'error': f'Error al cargar productos: {str(e)}'
        })

def fijaciones(request):
    try:
        categoria = Categoria.objects.filter(nombre='Fijaciones').first()
        if not categoria:
            return render(request, 'pages/fijaciones.html', {
                'productos': [],
                'error': 'Categoría "Fijaciones" no encontrada'
            })
        
        productos = Producto.objects.filter(categoria=categoria, en_venta=True)
        return render(request, 'pages/fijaciones.html', {'productos': productos})
    
    except Exception as e:
        return render(request, 'pages/fijaciones.html', {
            'productos': [],
            'error': f'Error al cargar productos: {str(e)}'
        })

def equipos_medicion(request):
    try:
        categoria = Categoria.objects.filter(nombre='Equipos de Medición').first()
        if not categoria:
            return render(request, 'pages/equipos-medicion.html', {
                'productos': [],
                'error': 'Categoría "Equipos de Medición" no encontrada'
            })
        
        productos = Producto.objects.filter(categoria=categoria, en_venta=True)
        return render(request, 'pages/equipos-medicion.html', {'productos': productos})
    
    except Exception as e:
        return render(request, 'pages/equipos-medicion.html', {
            'productos': [],
            'error': f'Error al cargar productos: {str(e)}'
        })

@secure_auth_view(rate='5/5m')
@honeypot_check
def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next') or '/'
    
    if request.method == 'POST':
        usuario = sanitize_html_input(request.POST.get('usuario', ''))
        password = request.POST.get('password', '')
        ip_address = request.META.get('REMOTE_ADDR', '')
        
        # Verificar si el login está bloqueado
        if is_login_blocked(usuario, ip_address):
            log_suspicious_activity(request, 'LOGIN_BLOCKED', f'Usuario: {usuario}')
            messages.error(request, "Demasiados intentos fallidos. Cuenta temporalmente bloqueada.")
            return render(request, 'pages/login.html', {
                'next': next_url,
                'usuario': usuario,
            })
        
        # Intentar autenticación
        user = authenticate(request, username=usuario, password=password)
        
        if user is not None:
            # Login exitoso
            clear_failed_login_attempts(usuario, ip_address)
            login(request, user)
            auth_logger.info(f"Login exitoso para usuario {usuario} desde IP {ip_address}")
            return redirect(next_url)
        else:
            # Login fallido
            track_failed_login(usuario, ip_address)
            security_logger.warning(f"Intento de login fallido para usuario {usuario} desde IP {ip_address}")
            messages.error(request, "Usuario o contraseña incorrectos.")
            return render(request, 'pages/login.html', {
                'next': next_url,
                'usuario': usuario,
            })
    
    return render(request, 'pages/login.html', {'next': next_url})

@secure_auth_view(rate='3/5m')
@honeypot_check
def register(request):
    # Temporalmente simplificada para evitar redirecciones
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.POST.get('nombre', '')
        usuario = request.POST.get('usuario', '')
        correo = request.POST.get('correo', '')
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        telefono = request.POST.get('telefono', '')
        
        # Validaciones básicas
        if not all([nombre, usuario, correo, password, password2, telefono]):
            messages.error(request, "Todos los campos son obligatorios.")
            return render(request, 'pages/register.html', {
                'nombre': nombre,
                'usuario': usuario,
                'correo': correo,
                'telefono': telefono,
            })
        
        if password != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'pages/register.html', {
                'nombre': nombre,
                'usuario': usuario,
                'correo': correo,
                'telefono': telefono,
            })
        
        # Verificar usuario único
        if User.objects.filter(username=usuario).exists():
            messages.error(request, "El usuario ya existe.")
            return render(request, 'pages/register.html', {
                'nombre': nombre,
                'usuario': usuario,
                'correo': correo,
                'telefono': telefono,
            })
        
        # Verificar email único
        if User.objects.filter(email=correo).exists():
            messages.error(request, "El correo ya está registrado.")
            return render(request, 'pages/register.html', {
                'nombre': nombre,
                'usuario': usuario,
                'correo': correo,
                'telefono': telefono,
            })
        
        try:
            # Crear usuario
            user = User.objects.create_user(
                username=usuario,
                email=correo,
                password=password,
                first_name=nombre
            )
            
            # Crear perfil de usuario
            usuario_profile = Usuario.objects.create(user=user, telefono=telefono)
            
            messages.success(request, "Usuario creado exitosamente. Ahora puedes iniciar sesión.")
            return redirect('app:login')
            
        except Exception as e:
            messages.error(request, f"Error al crear el usuario: {str(e)}")
            return render(request, 'pages/register.html', {
                'nombre': nombre,
                'usuario': usuario,
                'correo': correo,
                'telefono': telefono,
            })
    
    return render(request, 'pages/register.html')

def checkout(request):
    discount_percentage = 0  # Por defecto sin descuento
    if request.user.is_authenticated:
        discount_percentage = 10  # Ejemplo de 10% de descuento para clientes logueados

    return render(request, 'pages/checkout.html', {
        'discount_percentage': discount_percentage,
        'user': request.user
    })

def logout_view(request):
    ip_address = request.META.get('REMOTE_ADDR', '')
    username = request.user.username if request.user.is_authenticated else 'Anónimo'
    
    logout(request)
    auth_logger.info(f"Logout de usuario {username} desde IP {ip_address}")
    
    # Redirigir a la página principal
    return redirect('app:index')

def productos_externos_page(request):
    try:
        productos = obtener_productos()
        
    except Exception as e:
        productos = []
    return render(request, 'pages/productos/productos-externos.html', {'productos': productos})

def valor_dolar_page(request):
    try:
        data = obtener_valor_dolar()
        return render(request, 'pages/banco_central/valor-dolar.html', {
            'valor': data['valor'],
            'fecha': data['fecha'],
            'error': None
        })
    except Exception as e:
        return render(request, 'pages/banco_central/valor-dolar.html', {
            'valor': None,
            'fecha': None,
            'error': str(e)
        })

@csrf_exempt
def crear_pago_page(request):
    init_point = None
    error = None

    if request.method == "POST":
        try:
            data = {
                "title": request.POST.get("title"),
                "quantity": int(request.POST.get("quantity")),
                "unit_price": float(request.POST.get("unit_price")),
                "success_url": "https://echoapi.io/success",
                "failure_url": "https://echoapi.io/failure",
                "pending_url": "https://echoapi.io/pending"
            }
            resultado = crear_preferencia_pago(data)
            init_point = resultado.get("init_point")
        except Exception as e:
            error = str(e)

    return render(request, 'pages/mercado_pago/crear_pago.html', {
        "init_point": init_point,
        "error": error
    })

@csrf_exempt
def procesar_pago(request):
    if request.method == 'POST':
        import json
        import random
        from datetime import datetime
        from decimal import Decimal
        from app.domain.models import Pago
        from django.contrib.auth.models import User
        
        try:
            data = json.loads(request.body)
            
            # Obtener datos del carrito
            productos = data.get('productos', [])
            metodo_pago = data.get('metodo_pago', 'tarjeta')
            
            # Para usuarios no autenticados, obtener datos del formulario
            datos_cliente = data.get('datos_cliente', {})
            
            if not productos:
                return JsonResponse({'error': 'Carrito vacío'}, status=400)
            
            # Calcular totales
            subtotal = Decimal('0.00')
            for producto in productos:
                precio = Decimal(str(producto['precio']))
                cantidad = int(producto['cantidad'])
                subtotal += precio * cantidad
            
            # Aplicar descuento solo si está autenticado
            descuento_porcentaje = Decimal('10.00') if request.user.is_authenticated else Decimal('0.00')
            descuento = subtotal * (descuento_porcentaje / 100)
            subtotal_con_descuento = subtotal - descuento
            
            # Calcular IVA (19%)
            iva = subtotal_con_descuento * Decimal('0.19')
            total = subtotal_con_descuento + iva
            
            # Generar número de voucher único
            numero_voucher = f"FRS{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
            
            # Determinar comprador y nombre
            if request.user.is_authenticated:
                comprador = request.user
                nombre_comprador = request.user.get_full_name() or request.user.username
            else:
                # Para usuarios no autenticados, usar None como comprador
                comprador = None
                nombre_comprador = datos_cliente.get('nombre', 'Cliente invitado')
            
            # Crear el pago
            pago = Pago.objects.create(
                comprador=comprador,
                metodo_pago=metodo_pago,
                subtotal=subtotal_con_descuento,
                iva=iva,
                descuento=descuento,
                total=total,
                productos_json=productos,
                numero_voucher=numero_voucher
            )
            
            # Guardar datos del voucher en la sesión para acceso seguro
            request.session['voucher_data'] = {
                'voucher_id': str(pago.id),
                'numero_voucher': numero_voucher,
                'fecha': pago.fecha.strftime('%d/%m/%Y %H:%M:%S'),
                'subtotal': float(subtotal),
                'descuento': float(descuento),
                'subtotal_con_descuento': float(subtotal_con_descuento),
                'iva': float(iva),
                'total': float(total),
                'metodo_pago': metodo_pago,
                'productos': productos,
                'comprador': nombre_comprador,
                'es_usuario_registrado': request.user.is_authenticated
            }
            request.session['voucher_access_allowed'] = True
            
            return JsonResponse({
                'success': True,
                'voucher_id': str(pago.id),
                'numero_voucher': numero_voucher,
                'fecha': pago.fecha.strftime('%d/%m/%Y %H:%M:%S'),
                'subtotal': float(subtotal),
                'descuento': float(descuento),
                'subtotal_con_descuento': float(subtotal_con_descuento),
                'iva': float(iva),
                'total': float(total),
                'metodo_pago': metodo_pago,
                'productos': productos,
                'comprador': nombre_comprador,
                'es_usuario_registrado': request.user.is_authenticated
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def crear_pago_externo_view(request):
    if request.method == 'POST':
        try:
            import json
            data_json = json.loads(request.body)
            data = {
                "title": data_json.get("title", "Producto de prueba"),
                "quantity": int(data_json.get("quantity", 1)),
                "unit_price": float(data_json.get("unit_price", 1000)),
                "success_url": data_json.get("success_url", "https://echoapi.io/success"),
                "failure_url": data_json.get("failure_url", "https://echoapi.io/failure"),
                "pending_url": data_json.get("pending_url", "https://echoapi.io/pending"),
            }
            resultado = crear_preferencia_pago(data)
            return JsonResponse(resultado)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Método no permitido"}, status=405)

def voucher_view(request, token=None):
    # Si se proporciona un token, validarlo
    if token:
        # Verificar que el token coincida con algún voucher en la sesión
        voucher_data = request.session.get('voucher_data', None)
        if not voucher_data or voucher_data.get('voucher_id') != token:
            messages.error(request, 'Token de voucher inválido.')
            return redirect('/')
    else:
        # Sin token, verificar acceso por sesión
        if not request.session.get('voucher_access_allowed', False):
            messages.error(request, 'No tienes permiso para acceder a esta página. Realiza una compra primero.')
            return redirect('/')
        
        voucher_data = request.session.get('voucher_data', None)
        if not voucher_data:
            messages.error(request, 'No se encontraron datos del voucher. Realiza una compra primero.')
            return redirect('/')
    
    # Opcional: Limpiar la sesión después de acceder (permite solo un acceso)
    # if not token:  # Solo limpiar si no es acceso por token
    #     del request.session['voucher_access_allowed']
    #     del request.session['voucher_data']
    
    return render(request, 'pages/voucher.html', {'voucher_data': voucher_data})

# Vista para limpiar rate limit (solo para desarrollo)
def clear_rate_limit(request):
    """Vista para limpiar el rate limit durante desarrollo"""
    if settings.DEBUG:
        from django.core.cache import cache
        ip_address = request.META.get('REMOTE_ADDR', '')
        
        # Limpiar cache de rate limit
        cache.clear()
        
        messages.success(request, f'Rate limit limpiado para IP {ip_address}')
        auth_logger.info(f"Rate limit manual cleared para IP {ip_address}")
        
        return redirect('app:login')
    else:
        return redirect('app:index')


