from fastapi import APIRouter

from app.productos.application import service
from app.productos.domain.schemas import Producto,ProductoCreate
router = APIRouter()


@router.get("/", response_model=list[Producto])
def listar_productos():
    return service.obtener_productos()


@router.post("/", response_model=Producto)
def agregar_producto(producto: ProductoCreate):
    return service.crear_producto(producto)