from pydantic import BaseModel
from typing import Optional

class CategoriaIn(BaseModel):
    nombre: str
    descripcion: Optional[str] = None  # Campo opcional para la descripción

class CategoriaOut(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None  # Campo opcional para la descripción

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
    categoria_id: int  # Aquí recibimos el id de la categoría

class ProductoOut(ProductoCreate):
    id: int
    categoria: CategoriaOut  # Incluimos la categoría asociada

    class Config:
        from_attributes = True
        exclude = {"categoria_id"}