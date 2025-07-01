"""
Configuración y utilidades para pruebas de API
"""
import requests
import time
from typing import Dict, Any, Optional

class APITestConfig:
    """Configuración para pruebas de API"""
    
    # URLs base
    FASTAPI_BASE_URL = "http://localhost:8001"
    DJANGO_BASE_URL = "http://localhost:8000"
    
    # Timeouts
    REQUEST_TIMEOUT = 10
    RETRY_ATTEMPTS = 3
    RETRY_DELAY = 1
    
    # Headers por defecto
    DEFAULT_HEADERS = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

class APITestHelpers:
    """Utilidades para pruebas de API"""
    
    @staticmethod
    def wait_for_api(url: str, timeout: int = 30) -> bool:
        """
        Esperar a que la API esté disponible
        
        Args:
            url: URL de la API
            timeout: Tiempo máximo de espera en segundos
            
        Returns:
            True si la API está disponible, False si no
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    return True
            except:
                pass
            time.sleep(2)
        
        return False
    
    @staticmethod
    def make_request_with_retry(
        method: str, 
        url: str, 
        max_retries: int = 3,
        **kwargs
    ) -> requests.Response:
        """
        Hacer request con reintentos automáticos
        
        Args:
            method: Método HTTP (GET, POST, etc.)
            url: URL del endpoint
            max_retries: Número máximo de reintentos
            **kwargs: Argumentos adicionales para requests
            
        Returns:
            Response de requests
        """
        for attempt in range(max_retries + 1):
            try:
                response = requests.request(method, url, **kwargs)
                return response
            except Exception as e:
                if attempt == max_retries:
                    raise e
                time.sleep(APITestConfig.RETRY_DELAY)
        
        raise Exception("Max retries exceeded")
    
    @staticmethod
    def validate_json_response(response: requests.Response) -> Dict[Any, Any]:
        """
        Validar que la respuesta sea JSON válido
        
        Args:
            response: Response de requests
            
        Returns:
            Datos JSON parseados
            
        Raises:
            AssertionError: Si la respuesta no es JSON válido
        """
        assert response.headers.get("content-type", "").startswith("application/json"), \
            f"Expected JSON response, got {response.headers.get('content-type')}"
        
        try:
            return response.json()
        except ValueError as e:
            raise AssertionError(f"Invalid JSON response: {e}")
    
    @staticmethod
    def validate_response_time(response: requests.Response, max_time: float = 5.0):
        """
        Validar tiempo de respuesta
        
        Args:
            response: Response de requests
            max_time: Tiempo máximo permitido en segundos
        """
        response_time = response.elapsed.total_seconds()
        assert response_time <= max_time, \
            f"Response time {response_time:.2f}s exceeds maximum {max_time}s"
    
    @staticmethod
    def validate_status_code(response: requests.Response, expected_code: int):
        """
        Validar código de estado HTTP
        
        Args:
            response: Response de requests
            expected_code: Código de estado esperado
        """
        assert response.status_code == expected_code, \
            f"Expected status {expected_code}, got {response.status_code}. Response: {response.text}"
    
    @staticmethod
    def validate_required_fields(data: Dict[Any, Any], required_fields: list):
        """
        Validar que los campos requeridos estén presentes
        
        Args:
            data: Datos a validar
            required_fields: Lista de campos requeridos
        """
        for field in required_fields:
            assert field in data, f"Required field '{field}' missing from response"
    
    @staticmethod
    def create_test_product() -> Dict[str, Any]:
        """
        Crear datos de producto para pruebas
        
        Returns:
            Diccionario con datos de producto
        """
        timestamp = int(time.time())
        return {
            "nombre": f"Producto Test {timestamp}",
            "descripcion": "Producto creado para pruebas automatizadas",
            "precio": 29.99,
            "stock": 10,
            "categoria_id": 1
        }
    
    @staticmethod
    def create_test_category() -> Dict[str, Any]:
        """
        Crear datos de categoría para pruebas
        
        Returns:
            Diccionario con datos de categoría
        """
        timestamp = int(time.time())
        return {
            "nombre": f"Categoría Test {timestamp}",
            "descripcion": "Categoría creada para pruebas automatizadas"
        }
    
    @staticmethod
    def create_test_payment() -> Dict[str, Any]:
        """
        Crear datos de pago para pruebas
        
        Returns:
            Diccionario con datos de pago
        """
        return {
            "titulo": "Producto de Prueba",
            "cantidad": 1,
            "precio": 100.00,
            "descripcion": "Pago de prueba automatizada"
        }

class APITestCleanup:
    """Utilidades para limpiar datos de prueba"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.created_products = []
        self.created_categories = []
    
    def add_product(self, product_id: int):
        """Añadir producto a la lista de limpieza"""
        self.created_products.append(product_id)
    
    def add_category(self, category_id: int):
        """Añadir categoría a la lista de limpieza"""
        self.created_categories.append(category_id)
    
    def cleanup_products(self):
        """Limpiar productos creados durante las pruebas"""
        for product_id in self.created_products:
            try:
                requests.delete(f"{self.base_url}/productos/{product_id}")
                print(f"🧹 Producto {product_id} eliminado")
            except:
                print(f"⚠️ No se pudo eliminar producto {product_id}")
        
        self.created_products.clear()
    
    def cleanup_categories(self):
        """Limpiar categorías creadas durante las pruebas"""
        for category_id in self.created_categories:
            try:
                requests.delete(f"{self.base_url}/productos/categorias/{category_id}")
                print(f"🧹 Categoría {category_id} eliminada")
            except:
                print(f"⚠️ No se pudo eliminar categoría {category_id}")
        
        self.created_categories.clear()
    
    def cleanup_all(self):
        """Limpiar todos los datos creados"""
        self.cleanup_products()
        self.cleanup_categories()
        print("🧹 Limpieza completada")
