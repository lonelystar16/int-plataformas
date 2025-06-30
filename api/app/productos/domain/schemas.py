from pydantic import BaseModel
from typing import Optional

class CategoriaIn(BaseModel):
    nombre: str
    descripcion: Optional[str] = None  

class CategoriaOut(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None  

    class Config:
        from_attributes = True

class ProductoCreate(BaseModel):
    nombre: str
    descripcion: str
    precio: float
    stock: int
    en_venta: bool
    sku: str
    destacado: bool
    descuento: int
    categoria_id: int 

class ProductoOut(ProductoCreate):
    id: int
    categoria: Optional[CategoriaOut] = None
    categoria_id: Optional[int] = None

    class Config:
        from_attributes = True