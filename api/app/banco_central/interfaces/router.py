from fastapi import APIRouter
from ..application.service import consultar_valor_dolar
from ..domain.schemas import Indicador

router = APIRouter()

@router.get("/valor-dolar", response_model=Indicador)
def get_valor_dolar():
    return consultar_valor_dolar()
