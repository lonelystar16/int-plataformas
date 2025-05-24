import requests 

class ExternalAPI:
    urlBase = "https://mindicador.cl/api/"
    @staticmethod
    def get_dolar_data():
        response= requests.get(ExternalAPI.urlBase + "dolar")
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()  # Return the JSON response
