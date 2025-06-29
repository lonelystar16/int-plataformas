from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.productos.infrastructure import repository
from app.productos.domain.schemas import ProductoCreate, ProductoOut,CategoriaIn,CategoriaOut# 


router = APIRouter()
# Rutas de Categorías
@router.post("/categorias/", response_model=CategoriaOut)
def crear_categoria(categoria: CategoriaIn, db: Session = Depends(get_db)):
    return repository.crear_categoria(db, categoria.model_dump())  # Cambié dict() por model_dump()

@router.get("/categorias/", response_model=List[CategoriaOut])
def listar_categorias(db: Session = Depends(get_db)):
    return repository.obtener_categorias(db)
    


@router.post("/", response_model=ProductoOut)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    return repository.crear_producto(db, producto.model_dump())  # Cambié dict() por model_dump()

@router.get("/", response_model=List[ProductoOut])
def listar_productos(db: Session = Depends(get_db)):
    productos = repository.obtener_productos(db)
    return productos