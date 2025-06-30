from typing import List, Optional
from app.domain.models import Producto, Categoria
from app.domain.repositories import ProductoRepositoryInterface, CategoriaRepositoryInterface


class GetProductosPorCategoriaUseCase:
    def __init__(self, producto_repository: ProductoRepositoryInterface, categoria_repository: CategoriaRepositoryInterface):
        self.producto_repository = producto_repository
        self.categoria_repository = categoria_repository
    
    def execute(self, categoria_nombre: str) -> tuple[List[Producto], Optional[str]]:
        """
        Obtiene productos por nombre de categoría
        Retorna: (lista_productos, mensaje_error)
        """
        try:
            categoria = self.categoria_repository.get_by_name(categoria_nombre)
            if not categoria:
                return [], f'Categoría "{categoria_nombre}" no encontrada'
            
            productos = self.producto_repository.get_by_categoria(categoria, en_venta=True)
            return productos, None
            
        except Exception as e:
            return [], f'Error al cargar productos: {str(e)}'


class CreateProductoUseCase:
    def __init__(self, producto_repository: ProductoRepositoryInterface):
        self.producto_repository = producto_repository
    
    def execute(self, producto_data: dict) -> tuple[Optional[Producto], Optional[str]]:
        """
        Crea un nuevo producto
        Retorna: (producto_creado, mensaje_error)
        """
        try:
            producto = self.producto_repository.create(producto_data)
            return producto, None
        except Exception as e:
            return None, f'Error al crear producto: {str(e)}'


class GetAllProductosUseCase:
    def __init__(self, producto_repository: ProductoRepositoryInterface):
        self.producto_repository = producto_repository
    
    def execute(self) -> List[Producto]:
        """
        Obtiene todos los productos
        """
        return self.producto_repository.get_all()


class GetAllCategoriasUseCase:
    def __init__(self, categoria_repository: CategoriaRepositoryInterface):
        self.categoria_repository = categoria_repository
    
    def execute(self) -> List[Categoria]:
        """
        Obtiene todas las categorías
        """
        return self.categoria_repository.get_all()
