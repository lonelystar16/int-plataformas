# Importar las dependencias necesarias
from sqlalchemy.orm import Session
from app.productos.domain.models_sql import ProductoDB,CategoriaDB




# Funciones para manejar categorías
def crear_categoria(db: Session, categoria_data: dict):
    nueva_categoria = CategoriaDB(**categoria_data)
    db.add(nueva_categoria)
    db.commit()
    db.refresh(nueva_categoria)
    return nueva_categoria

def obtener_categoria(db: Session, categoria_id: int):
    return db.query(CategoriaDB).all()

def crear_producto(db: Session, producto_data: dict):
    # Verificar si la categoría existe
    categoria = db.query(CategoriaDB).filter(CategoriaDB.id == producto_data["categoria_id"]).first()

    if not categoria:
        raise ValueError("La categoría no existe.")

    # Crear el nuevo producto
    nuevo_producto = ProductoDB(**producto_data)
    nuevo_producto.categoria_id = categoria.id
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)

    # Devolver el producto creado con la categoría asociada
    return nuevo_producto



def obtener_categorias(db: Session):
    return db.query(CategoriaDB).all()

# ----- 
# Funciones para manejar productos
def obtener_productos(db: Session):
    return db.query(ProductoDB).all()

def guardar_producto(db: Session, producto: ProductoDB):
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto
