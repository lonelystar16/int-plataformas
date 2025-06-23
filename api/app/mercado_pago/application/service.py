from ..domain.schemas import PreferenciaRequest, PreferenciaResponse
from ..infrastructure.repository import crear_preferencia

def generar_preferencia_pago(data: PreferenciaRequest) -> PreferenciaResponse:
    payload = {
        "items": [
            {
                "title": data.title,
                "quantity": data.quantity,
                "unit_price": data.unit_price
            }
        ],
        "back_urls": {
            "success": data.success_url,
            "failure": data.failure_url,
            "pending": data.pending_url
        },
        "auto_return": "approved"
    }
    resultado = crear_preferencia(payload)
    return PreferenciaResponse(init_point=resultado["init_point"], id=resultado["id"])
