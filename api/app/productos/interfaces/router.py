from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.productos.infrastructure import repository
from app.productos.domain.schemas import ProductoCreate, ProductoOut, CategoriaIn, CategoriaOut

router = APIRouter()
# Rutas de Categorías


# * Metodo GET para obtener todas las categorías
@router.get("/categorias/", response_model=List[CategoriaOut])
def listar_categorias(db: Session = Depends(get_db)):
    """Obtiene todas las categorías."""
    categorias = repository.obtener_categorias(db)
    return categorias




#* Metodo POST para crear una categoría
@router.post("/categorias/", response_model=CategoriaOut)
def crear_categoria(categoria: CategoriaIn, db: Session = Depends(get_db)):
    return repository.crear_categoria(db, categoria.model_dump())

# * Metodo DELETE para eliminar una categoría por ID
@router.delete("/categorias/{categoria_id}", status_code=204)
def eliminar_categoria_endpoint(categoria_id: int, db: Session = Depends(get_db)):
    """Elimina una categoría por su ID."""
    # Verificar si la categoría existe
    categoria = repository.obtener_categoria_por_id(db, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    repository.eliminar_categoria(db, categoria_id)

# # Rutas de Productos
# * Metodo POST para crear un producto
@router.post("/", response_model=ProductoOut)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    return repository.crear_producto(db, producto.model_dump())

# * Metodo GET para obtener todos los productos
@router.get("/", response_model=List[ProductoOut])
def listar_productos(db: Session = Depends(get_db)):
    productos = repository.obtener_productos(db)
    return productos

# * Metodo DELETE para eliminar un producto por ID
@router.delete("/{producto_id}", status_code=204)
def eliminar_producto_endpoint(producto_id: int, db: Session = Depends(get_db)):
    """Elimina un producto por su ID."""
    # Verificar si el producto existe
    producto = repository.obtener_producto_por_id(db, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")