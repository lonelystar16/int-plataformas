import datetime

import json
import os
from typing import List
from app.productos.domain.schemas import Producto

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'productos.json')

def default_serializer(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")





def cargar_productos() -> List[Producto]:
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [Producto(**item) for item in data]
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def guardar_producto(producto: Producto) -> None:
    productos = cargar_productos()
    productos.append(producto)
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(
    [p.model_dump() for p in productos],
    f,
    indent=4,
    ensure_ascii=False,
    default=default_serializer
)
