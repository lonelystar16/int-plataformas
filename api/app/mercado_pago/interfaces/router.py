from fastapi import APIRouter
from ..domain.schemas import PreferenciaRequest, PreferenciaResponse
from ..application.service import generar_preferencia_pago

router = APIRouter()

@router.post("/crear-pago", response_model=PreferenciaResponse)
def crear_pago(preferencia: PreferenciaRequest):
    return generar_preferencia_pago(preferencia)
