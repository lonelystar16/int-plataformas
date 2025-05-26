from django.shortcuts import render, redirect
from rest_framework import viewsets, permissions
from ..domain.models import Producto, Categoria
from .serializers import ProductoSerializer, CategoriaSerializer
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from app.domain.models import Usuario
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app.db.external_api import obtener_valor_dolar_actual

def index(request):
    return render(request, 'pages/mainPage.html')

def herra_manuales(request):
    productos = Producto.objects.filter(categoria__nombre="Herramientas Manuales", en_venta=True)
    return render(request, 'pages/herra-manuales.html', {'productos': productos})

def materiales_basicos(request):
    productos = Producto.objects.filter(categoria__nombre="Materiales Básicos", en_venta=True)
    return render(request, 'pages/materiales-basicos.html', {'productos': productos})

def equipos_seguridad(request):
    productos = Producto.objects.filter(categoria__nombre="Equipos Seguridad", en_venta=True)
    return render(request, 'pages/equipos-seguridad.html', {'productos': productos})

def tornillos_anclaje(request):
    productos = Producto.objects.filter(categoria__nombre="Tornillos y Anclajes", en_venta=True)
    return render(request, 'pages/tornillos-anclaje.html', {'productos': productos})

def fijaciones(request):
    productos = Producto.objects.filter(categoria__nombre="Fijaciones y Adhesivos", en_venta=True)
    return render(request, 'pages/fijaciones.html', {'productos': productos})

def equipos_medicion(request):
    productos = Producto.objects.filter(categoria__nombre="Equipos de Medición", en_venta=True)
    return render(request, 'pages/equipos-medicion.html', {'productos': productos})

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


class DolarAPIView(APIView):
    def get(self, request):
        resultado = obtener_valor_dolar_actual()
        if resultado:
            return Response(resultado)
        return Response({"error": "No se pudo obtener el valor del dólar."},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE)

def logout_view(request):
    logout(request)
    # Puedes redirigir a la página principal, login, o donde prefieras
    return redirect('index')

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = CategoriaSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ProductoSerializer

