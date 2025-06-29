from app.productos.domain.schemas import ProductoOut
from app.productos.infrastructure import repository
from datetime import datetime
from app.productos.domain.schemas import ProductoCreate, Producto
def obtener_productos():
    return repository.cargar_productos()

contador_id = 1

def crear_producto(producto: ProductoCreate) -> Producto:
    global contador_id
    ahora = datetime.now()
    nuevo = Producto(
        id=contador_id,
        categoria=None,
        fecha_creacion=ahora,
        fecha_actualizacion=ahora,
        precio_final=producto.precio * (1 - producto.descuento / 100),
        **producto.dict()
    )
    contador_id += 1
    repository.guardar_producto(nuevo)
    return nuevo
