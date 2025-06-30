from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models import Producto, Categoria


class ProductoRepositoryInterface(ABC):
    @abstractmethod
    def get_all(self) -> List[Producto]:
        pass
    
    @abstractmethod
    def get_by_id(self, producto_id: int) -> Optional[Producto]:
        pass
    
    @abstractmethod
    def get_by_categoria(self, categoria: Categoria, en_venta: bool = True) -> List[Producto]:
        pass
    
    @abstractmethod
    def create(self, producto_data: dict) -> Producto:
        pass
    
    @abstractmethod
    def update(self, producto_id: int, producto_data: dict) -> Optional[Producto]:
        pass
    
    @abstractmethod
    def delete(self, producto_id: int) -> bool:
        pass


class CategoriaRepositoryInterface(ABC):
    @abstractmethod
    def get_all(self) -> List[Categoria]:
        pass
    
    @abstractmethod
    def get_by_id(self, categoria_id: int) -> Optional[Categoria]:
        pass
    
    @abstractmethod
    def get_by_name(self, nombre: str) -> Optional[Categoria]:
        pass
    
    @abstractmethod
    def create(self, categoria_data: dict) -> Categoria:
        pass
