from django.shortcuts import render
from rest_framework import viewsets, permissions
from ..domain.models import Producto, Categoria
from .serializers import ProductoSerializer, CategoriaSerializer

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

def login (request):
    return render(request, 'pages/login.html')

def register (request):
    return render(request, 'pages/register.html')

def checkout(request):
    return render(request, 'pages/checkout.html')

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = CategoriaSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ProductoSerializer

