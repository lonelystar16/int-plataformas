import requests

def obtener_valor_dolar_actual():
    url = "https://mindicador.cl/api/dolar"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        serie = data.get("serie", [])
        if serie:
            return {
                "fecha": serie[0].get("fecha"),
                "valor": serie[0].get("valor")
            }
    except requests.RequestException as e:
        print(f"Error al conectar con mindicador.cl: {e}")
    return None
