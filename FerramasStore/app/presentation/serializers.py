from rest_framework import serializers
from app.domain.models import Producto, Categoria

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'
        read_only_fields = ['id']
        

class ProductoSerializer(serializers.ModelSerializer):
    categoria = serializers.PrimaryKeyRelatedField(queryset=Categoria.objects.all())

    class Meta:
        model = Producto
        fields = '__all__'
        read_only_fields = ['id']
        
