import mercadopago
import os

ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN", "TEST-1088321424798390-052622-b2d5fdbf8c9512ea8edd080fafe66d38-794550145")

sdk = mercadopago.SDK(ACCESS_TOKEN)

def crear_preferencia(preferencia_data: dict) -> dict:
    try:
        resultado = sdk.preference().create(preferencia_data)
        return resultado["response"]
    except Exception as e:
        raise Exception(f"Error al crear preferencia: {str(e)}")
