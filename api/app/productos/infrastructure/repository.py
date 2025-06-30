# Importar las dependencias necesarias
from sqlalchemy.orm import Session, joinedload
from app.productos.domain.models_sql import ProductoDB,CategoriaDB

# Funciones para manejar categorías
def crear_categoria(db: Session, categoria_data: dict):
    nueva_categoria = CategoriaDB(**categoria_data)
    db.add(nueva_categoria)
    db.commit()
    db.refresh(nueva_categoria)
    return nueva_categoria

def obtener_categorias(db: Session):
    """
    Devuelve todas las categorías de la base de datos.
    """
    return db.query(CategoriaDB).all()


def obtener_categoria_por_id(db: Session, categoria_id: int):
    return db.query(CategoriaDB).filter(CategoriaDB.id == categoria_id).first()

def eliminar_categoria(db: Session, categoria_id: int):
    """
    Encuentra y elimina una categoría de la base de datos por su ID.
    """
    categoria_a_eliminar = db.query(CategoriaDB).filter(CategoriaDB.id == categoria_id).first()
    if categoria_a_eliminar:
        db.delete(categoria_a_eliminar)
        db.commit()
    return categoria_a_eliminar

# ----------------------------------------------------------------------


# Funciones para manejar productos
# * Metodo GET
def obtener_productos(db: Session):
    """ Obtiene todos los productos y carga su información de categoróa de forma eficiente. """
    return db.query(ProductoDB).options(joinedload(ProductoDB.categoria)).all()
def guardar_producto(db: Session, producto: ProductoDB):
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto
# * Metodo GET por ID
def obtener_producto_por_id(db: Session, producto_id: int):
    return db.query(ProductoDB).filter(ProductoDB.id == producto_id).first()
# * Metodo POST
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
# * Metodo PUT
def actualizar_producto(db: Session, producto_id: int, producto_data: dict):
    producto = db.query(ProductoDB).filter(ProductoDB.id == producto_id).first()
    if not producto:
        return None

    # Actualizar los campos del producto
    for key, value in producto_data.items():
        setattr(producto, key, value)

    db.commit()
    db.refresh(producto)
    return producto
# * Metodo DELETE
def eliminar_producto(db: Session, producto_id: int):
    producto_a_eliminar = db.query(ProductoDB).filter(ProductoDB.id == producto_id).first()
    if producto_a_eliminar:
        db.delete(producto_a_eliminar)
        db.commit()
    return producto_a_eliminar