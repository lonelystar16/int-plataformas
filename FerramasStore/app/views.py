from django.shortcuts import render
from rest_framework import viewsets, permissions
from app.domain.models import Producto, Categoria
from app.presentation.serializers import ProductoSerializer, CategoriaSerializer
from app.domain.services.api_externa import obtener_productos, obtener_valor_dolar
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

