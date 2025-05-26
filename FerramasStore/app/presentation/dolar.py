import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

class DolarView(APIView):
    permission_classes = [permissions.AllowAny]
    """
    API que retorna el valor actual del dólar desde mindicador.cl
    """
    def get(self, request):
        try:
            response = requests.get('https://mindicador.cl/api/dolar')
            if response.status_code == 200:
                data = response.json()
                valor_dolar = data['serie'][0]['valor']
                fecha = data['serie'][0]['fecha']
                return Response({
                    'valor_dolar': valor_dolar,
                    'fecha': fecha
                })
            else:
                return Response({'error': 'No se pudo obtener el valor del dólar'}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)