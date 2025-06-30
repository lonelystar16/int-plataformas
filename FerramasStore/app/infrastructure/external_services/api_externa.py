import requests

API_BASE = "http://127.0.0.1:8001"

def crear_preferencia_pago(data: dict) -> dict:
    url = f"{API_BASE}/mercado-pago/crear"
    response = requests.post(url, json=data)
    response.raise_for_status()
    return response.json()


def obtener_productos():
    url = f"{API_BASE}/productos/"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def obtener_valor_dolar():
    url = "http://127.0.0.1:8001/banco-central/"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
