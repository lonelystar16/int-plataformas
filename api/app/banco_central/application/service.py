from ..infrastructure.repository import obtener_dolar_actual
from ..domain.schemas import Indicador

def consultar_valor_dolar():
    data = obtener_dolar_actual()
    return Indicador(**data)
