
# FerramasStore/app/presentation/views.py
from ..domain.models import Producto, Categoria
from .serializers import ProductoSerializer, CategoriaSerializer
# Django imports
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
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
        return redirect(f'/login/?next={next_url}')
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
    return redirect('index')

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
        

