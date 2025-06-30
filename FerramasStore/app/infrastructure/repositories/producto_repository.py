from typing import List, Optional
from app.domain.models import Producto, Categoria
from app.domain.repositories import ProductoRepositoryInterface, CategoriaRepositoryInterface


class DjangoProductoRepository(ProductoRepositoryInterface):
    def get_all(self) -> List[Producto]:
        return list(Producto.objects.all())
    
    def get_by_id(self, producto_id: int) -> Optional[Producto]:
        try:
            return Producto.objects.get(id=producto_id)
        except Producto.DoesNotExist:
            return None
    
    def get_by_categoria(self, categoria: Categoria, en_venta: bool = True) -> List[Producto]:
        return list(Producto.objects.filter(categoria=categoria, en_venta=en_venta))
    
    def create(self, producto_data: dict) -> Producto:
        return Producto.objects.create(**producto_data)
    
    def update(self, producto_id: int, producto_data: dict) -> Optional[Producto]:
        try:
            producto = Producto.objects.get(id=producto_id)
            for field, value in producto_data.items():
                setattr(producto, field, value)
            producto.save()
            return producto
        except Producto.DoesNotExist:
            return None
    
    def delete(self, producto_id: int) -> bool:
        try:
            producto = Producto.objects.get(id=producto_id)
            producto.delete()
            return True
        except Producto.DoesNotExist:
            return False


class DjangoCategoriaRepository(CategoriaRepositoryInterface):
    def get_all(self) -> List[Categoria]:
        return list(Categoria.objects.all())
    
    def get_by_id(self, categoria_id: int) -> Optional[Categoria]:
        try:
            return Categoria.objects.get(id=categoria_id)
        except Categoria.DoesNotExist:
            return None
    
    def get_by_name(self, nombre: str) -> Optional[Categoria]:
        try:
            return Categoria.objects.get(nombre=nombre)
        except Categoria.DoesNotExist:
            return None
    
    def create(self, categoria_data: dict) -> Categoria:
        return Categoria.objects.create(**categoria_data)
