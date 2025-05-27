from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
import mercadopago



ACCESS_TOKEN = "TEST-1088321424798390-052622-b2d5fdbf8c9512ea8edd080fafe66d38-794550145"
class MercadoPagoInitView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        sdk = mercadopago.SDK(ACCESS_TOKEN)
        success_url = request.data.get("success_url") or "https://echoapi.io/success"
        failure_url = request.data.get("failure_url") or "https://echoapi.io/failure"
        pending_url = request.data.get("pending_url") or "https://echoapi.io/pending"
        preference_data = {
            "items": [
                {
                    "title": request.data.get("title", "Producto de prueba"),
                    "quantity": int(request.data.get("quantity", 1)),
                    "unit_price": float(request.data.get("unit_price", 1000))
                }
            ],
            "back_urls": {
                "success": success_url,
                "failure": failure_url,
                "pending": pending_url
            },
            "auto_return": "approved"
        }
        try:
            preference_response = sdk.preference().create(preference_data)
            print(preference_response)
            return Response({
                "init_point": preference_response["response"]["init_point"],
                "id": preference_response["response"]["id"]
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)