# FerramasStore/app/presentation/views.py
from ..domain.models import Producto, Categoria
from .serializers import ProductoSerializer, CategoriaSerializer
# Django imports
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
# Django REST Framework imports
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# Clean Architecture imports
from app.application.use_cases.producto_use_cases import GetProductosPorCategoriaUseCase
from app.infrastructure.repositories.producto_repository import DjangoProductoRepository, DjangoCategoriaRepository
# External API services
from app.infrastructure.external_services.api_externa import obtener_valor_dolar, obtener_productos, crear_preferencia_pago

# Dependency injection
producto_repository = DjangoProductoRepository()
categoria_repository = DjangoCategoriaRepository()
get_productos_por_categoria_use_case = GetProductosPorCategoriaUseCase(producto_repository, categoria_repository)

def index(request):
    return render(request, 'pages/mainPage.html')

def herra_manuales(request):
    productos, error = get_productos_por_categoria_use_case.execute("Herramientas Manuales")
    context = {'productos': productos}
    if error:
        context['error'] = error
    return render(request, 'pages/herra-manuales.html', context)

def materiales_basicos(request):
    productos, error = get_productos_por_categoria_use_case.execute("Materiales Básicos")
    context = {'productos': productos}
    if error:
        context['error'] = error
    return render(request, 'pages/materiales-basicos.html', context)

def equipos_seguridad(request):
    productos, error = get_productos_por_categoria_use_case.execute("Equipos de Seguridad")
    context = {'productos': productos}
    if error:
        context['error'] = error
    return render(request, 'pages/equipos-seguridad.html', context)

def tornillos_anclaje(request):
    productos, error = get_productos_por_categoria_use_case.execute("Tornillos y Anclajes")
    context = {'productos': productos}
    if error:
        context['error'] = error
    return render(request, 'pages/tornillos-anclaje.html', context)

def fijaciones(request):
    productos, error = get_productos_por_categoria_use_case.execute("Fijaciones")
    context = {'productos': productos}
    if error:
        context['error'] = error
    return render(request, 'pages/fijaciones.html', context)

def equipos_medicion(request):
    productos, error = get_productos_por_categoria_use_case.execute("Equipos de Medición")
    context = {'productos': productos}
    if error:
        context['error'] = error
    return render(request, 'pages/equipos-medicion.html', context)

def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next') or '/checkout/'
    if request.method == 'POST':
        usuario = request.POST['usuario']
        password = request.POST['password']
        user = authenticate(request, username=usuario, password=password)
        if user is not None:
            login(request, user)
            return redirect(next_url)
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
            return render(request, 'pages/login.html', {
                'next': next_url,
                'usuario': usuario,
            })
    return render(request, 'pages/login.html', {'next': next_url})

def register(request):
    next_url = request.GET.get('next') or request.POST.get('next') or '/checkout/'
    if request.method == 'POST':
        nombre = request.POST['nombre']
        usuario = request.POST['usuario']
        correo = request.POST['correo']
        password = request.POST['password']
        password2 = request.POST['password2']
        telefono = request.POST['telefono']

        if password != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'pages/register.html', {
                'next': next_url,
                'nombre': nombre,
                'usuario': usuario,
                'correo': correo,
                'telefono': telefono,
            })

        if User.objects.filter(username=usuario).exists():
            messages.error(request, "El usuario ya existe.")
            return render(request, 'pages/register.html', {
                'next': next_url,
                'nombre': nombre,
                'usuario': usuario,
                'correo': correo,
                'telefono': telefono,
            })

        if User.objects.filter(email=correo).exists():
            messages.error(request, "El correo ya está registrado.")
            return render(request, 'pages/register.html', {
                'next': next_url,
                'nombre': nombre,
                'usuario': usuario,
                'correo': correo,
                'telefono': telefono,
            })

        user = User.objects.create_user(
            username=usuario,
            email=correo,
            password=password,
            first_name=nombre
        )
        user.usuario.telefono = telefono
        user.usuario.save()

        # Redirigir a login con next
        return redirect(f'/auth/login/?next={next_url}')
    return render(request, 'pages/register.html', {'next': next_url})

def checkout(request):
    discount_percentage = 0  # Por defecto sin descuento
    if request.user.is_authenticated:
        discount_percentage = 10  # Ejemplo de 10% de descuento para clientes logueados

    return render(request, 'pages/checkout.html', {
        'discount_percentage': discount_percentage,
        'user': request.user
    })

def logout_view(request):
    logout(request)
    # Puedes redirigir a la página principal, login, o donde prefieras
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

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = CategoriaSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ProductoSerializer

class CrearPagoExternoView(APIView):
    def post(self, request):
        try:
            data = {
                "title": request.data.get("title", "Producto de prueba"),
                "quantity": int(request.data.get("quantity", 1)),
                "unit_price": float(request.data.get("unit_price", 1000)),
                "success_url": request.data.get("success_url", "https://echoapi.io/success"),
                "failure_url": request.data.get("failure_url", "https://echoapi.io/failure"),
                "pending_url": request.data.get("pending_url", "https://echoapi.io/pending"),
            }
            resultado = crear_preferencia_pago(data)
            return Response(resultado)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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


