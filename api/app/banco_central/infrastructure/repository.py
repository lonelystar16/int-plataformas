import httpx

def obtener_dolar_actual():
    url = "https://mindicador.cl/api/dolar"
    response = httpx.get(url)
    if response.status_code == 200:
        data = response.json()
        serie = data["serie"][0]
        return {
            "valor": serie["valor"],
            "fecha": serie["fecha"]
        }
    else:
        raise Exception("Error al consultar el valor del dólar")
