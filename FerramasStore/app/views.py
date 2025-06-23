from django.shortcuts import render
from rest_framework import viewsets, permissions
from app.domain.models import Producto, Categoria
from app.presentation.serializers import ProductoSerializer, CategoriaSerializer
from app.domain.services.api_externa import obtener_productos, obtener_valor_dolar
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

def productos_externos(request):
    try:
        productos = obtener_productos()
    except Exception as e:
        productos = []
    return render(request, 'pages/productos/productos_externos.html', {'productos': productos})

def valor_dolar_page(request):
    try:
        data = obtener_valor_dolar()
        return render(request, 'pages/valor_dolar.html', {
            'valor': data['valor'],
            'fecha': data['fecha'],
            'error': None
        })
    except Exception as e:
        return render(request, 'pages/valor_dolar.html', {
            'valor': None,
            'fecha': None,
            'error': str(e)
        })

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = CategoriaSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ProductoSerializer

