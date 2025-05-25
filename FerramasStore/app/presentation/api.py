from FerramasStore.app.domain.models import Producto, Categoria
from rest_framework import viewsets, permissions
from .serializers import ProductoSerializer, CategoriaSerializer

class CategoriaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows categories to be viewed or edited.
    """
    queryset = Categoria.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = CategoriaSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows products to be viewed or edited.
    """
    queryset = Producto.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ProductoSerializer