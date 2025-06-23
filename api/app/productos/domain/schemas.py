from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProductoCreate(BaseModel):
    nombre: str
    descripcion: str
    precio: float
    stock: int
    en_venta: bool
    sku: str
    destacado: bool
    descuento: int





class Producto(ProductoCreate):
    id: int
    categoria: Optional[str] = None
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    precio_final: float
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }