from django.shortcuts import render
from rest_framework import viewsets, permissions
from app.domain.models import Producto, Categoria
from app.presentation.serializers import ProductoSerializer, CategoriaSerializer

def index(request):
    return render(request, 'pages/mainPage.html')

def herra_manuales(request):
    return render(request, 'pages/herra-manuales.html')

def materiales_basicos(request):
    return render(request, 'pages/materiales-basicos.html')

def equipos_seguridad(request):
    return render(request, 'pages/equipos-seguridad.html')

def tornillos_anclaje(request):
    return render(request, 'pages/tornillos-anclaje.html')

def fijaciones(request):
    return render(request, 'pages/fijaciones.html')

def equipos_medicion(request):
    return render(request, 'pages/equipos-medicion.html')

def login(request):
    return render(request, 'pages/login.html')

def register(request):
    return render(request, 'pages/register.html')

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = CategoriaSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ProductoSerializer

