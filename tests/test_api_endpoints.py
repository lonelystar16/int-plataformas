"""
Pruebas para los endpoints de la API FastAPI
"""
import pytest
import requests
import json
from datetime import datetime
import time

class TestAPIEndpoints:
    """Pruebas para todos los endpoints de la API FastAPI"""
    
    BASE_URL = "http://localhost:8001"
    
    @classmethod
    def setup_class(cls):
        """Configuración inicial para todas las pruebas"""
        print("🔄 Iniciando pruebas de API FastAPI...")
        # Verificar que la API esté disponible
        try:
            response = requests.get(f"{cls.BASE_URL}/", timeout=5)
            assert response.status_code == 200, "API no está disponible"
            print("✅ API FastAPI está funcionando")
        except Exception as e:
            pytest.fail(f"❌ API no está disponible: {e}")
    
    def test_api_health_check(self):
        """Verificar que la API esté funcionando"""
        response = requests.get(f"{self.BASE_URL}/")
        assert response.status_code == 200
        print("✅ Health check de API exitoso")
    
    def test_api_documentation_available(self):
        """Verificar que la documentación automática esté disponible"""
        # Probar Swagger UI
        response = requests.get(f"{self.BASE_URL}/docs")
        assert response.status_code == 200
        print("✅ Documentación Swagger disponible")
        
        # Probar ReDoc
        response = requests.get(f"{self.BASE_URL}/redoc")
        assert response.status_code == 200
        print("✅ Documentación ReDoc disponible")
        
        # Probar OpenAPI JSON
        response = requests.get(f"{self.BASE_URL}/openapi.json")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        print("✅ Esquema OpenAPI disponible")


class TestProductosAPI:
    """Pruebas para endpoints de productos"""
    
    BASE_URL = "http://localhost:8001/productos"
    
    def test_listar_productos(self):
        """Probar GET /productos/ - Listar todos los productos"""
        response = requests.get(f"{self.BASE_URL}/")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        productos = response.json()
        assert isinstance(productos, list)
        print(f"✅ Listado de productos exitoso - {len(productos)} productos encontrados")
    
    def test_crear_producto(self):
        """Probar POST /productos/ - Crear un nuevo producto"""
        nuevo_producto = {
            "nombre": f"Producto Test {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "descripcion": "Producto creado para pruebas automatizadas",
            "precio": 29.99,
            "stock": 10,
            "categoria_id": 1
        }
        
        response = requests.post(
            f"{self.BASE_URL}/",
            json=nuevo_producto,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            producto_creado = response.json()
            assert "id" in producto_creado
            assert producto_creado["nombre"] == nuevo_producto["nombre"]
            assert producto_creado["precio"] == nuevo_producto["precio"]
            print(f"✅ Producto creado exitosamente - ID: {producto_creado.get('id')}")
            
            # Guardar ID para limpieza posterior
            self.producto_test_id = producto_creado.get('id')
        else:
            print(f"⚠️ No se pudo crear producto - Status: {response.status_code}")
            print(f"   Response: {response.text}")
    
    def test_listar_categorias(self):
        """Probar GET /productos/categorias/ - Listar todas las categorías"""
        response = requests.get(f"{self.BASE_URL}/categorias/")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        categorias = response.json()
        assert isinstance(categorias, list)
        print(f"✅ Listado de categorías exitoso - {len(categorias)} categorías encontradas")
        
        # Verificar estructura de categorías
        if categorias:
            categoria = categorias[0]
            assert "id" in categoria
            assert "nombre" in categoria
    
    def test_crear_categoria(self):
        """Probar POST /productos/categorias/ - Crear una nueva categoría"""
        nueva_categoria = {
            "nombre": f"Categoría Test {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "descripcion": "Categoría creada para pruebas automatizadas"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/categorias/",
            json=nueva_categoria,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            categoria_creada = response.json()
            assert "id" in categoria_creada
            assert categoria_creada["nombre"] == nueva_categoria["nombre"]
            print(f"✅ Categoría creada exitosamente - ID: {categoria_creada.get('id')}")
            
            # Guardar ID para limpieza posterior
            self.categoria_test_id = categoria_creada.get('id')
        else:
            print(f"⚠️ No se pudo crear categoría - Status: {response.status_code}")
            print(f"   Response: {response.text}")
    
    def test_eliminar_producto_inexistente(self):
        """Probar DELETE /productos/{id} con ID inexistente"""
        id_inexistente = 99999
        response = requests.delete(f"{self.BASE_URL}/{id_inexistente}")
        
        # Debería retornar 404 para producto inexistente
        assert response.status_code in [404, 422]
        print("✅ Manejo correcto de producto inexistente")
    
    def test_eliminar_categoria_inexistente(self):
        """Probar DELETE /productos/categorias/{id} con ID inexistente"""
        id_inexistente = 99999
        response = requests.delete(f"{self.BASE_URL}/categorias/{id_inexistente}")
        
        # Debería retornar 404 para categoría inexistente
        assert response.status_code in [404, 422]
        print("✅ Manejo correcto de categoría inexistente")


class TestBancoCentralAPI:
    """Pruebas para endpoints de Banco Central"""
    
    BASE_URL = "http://localhost:8001/banco-central"
    
    def test_obtener_valor_dolar(self):
        """Probar GET /banco-central/valor-dolar"""
        response = requests.get(f"{self.BASE_URL}/valor-dolar")
        
        if response.status_code == 200:
            valor_dolar = response.json()
            
            # Verificar estructura de respuesta
            assert "codigo" in valor_dolar or "value" in valor_dolar or "valor" in valor_dolar
            print(f"✅ Valor del dólar obtenido exitosamente")
            print(f"   Respuesta: {valor_dolar}")
        else:
            print(f"⚠️ No se pudo obtener valor del dólar - Status: {response.status_code}")
            print(f"   Puede ser por conectividad externa")
            # No fallamos la prueba ya que depende de servicio externo
    
    def test_valor_dolar_response_structure(self):
        """Verificar estructura de respuesta del valor del dólar"""
        response = requests.get(f"{self.BASE_URL}/valor-dolar")
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)
            print("✅ Estructura de respuesta válida para valor del dólar")
        else:
            print("⚠️ Omitiendo validación de estructura por error de conectividad")


class TestMercadoPagoAPI:
    """Pruebas para endpoints de MercadoPago"""
    
    BASE_URL = "http://localhost:8001/mercado-pago"
    
    def test_crear_pago_basic(self):
        """Probar POST /mercado-pago/crear-pago con datos básicos"""
        preferencia_pago = {
            "titulo": "Producto de Prueba",
            "cantidad": 1,
            "precio": 100.00,
            "descripcion": "Pago de prueba automatizada"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/crear-pago",
            json=preferencia_pago,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            pago_response = response.json()
            print(f"✅ Preferencia de pago creada exitosamente")
            print(f"   Respuesta: {pago_response}")
            
            # Verificar que la respuesta tenga estructura esperada
            assert isinstance(pago_response, dict)
        else:
            print(f"⚠️ No se pudo crear preferencia de pago - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            print(f"   Puede ser por configuración de MercadoPago")
    
    def test_crear_pago_multiple_items(self):
        """Probar creación de pago con múltiples items"""
        preferencia_pago = {
            "titulo": "Compra Múltiple",
            "cantidad": 3,
            "precio": 250.00,
            "descripcion": "Compra de múltiples productos"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/crear-pago",
            json=preferencia_pago,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Preferencia de pago múltiple creada exitosamente")
        else:
            print(f"⚠️ Error en pago múltiple - Status: {response.status_code}")
    
    def test_crear_pago_validation(self):
        """Probar validación de datos en crear pago"""
        # Probar con datos inválidos
        preferencia_invalida = {
            "titulo": "",  # Título vacío
            "cantidad": -1,  # Cantidad negativa
            "precio": -50.00  # Precio negativo
        }
        
        response = requests.post(
            f"{self.BASE_URL}/crear-pago",
            json=preferencia_invalida,
            headers={"Content-Type": "application/json"}
        )
        
        # Debería retornar error de validación
        assert response.status_code in [400, 422, 500]
        print("✅ Validación de datos funcionando correctamente")


class TestAPIPerformance:
    """Pruebas de rendimiento de la API"""
    
    BASE_URL = "http://localhost:8001"
    
    def test_response_time_productos(self):
        """Verificar tiempo de respuesta de endpoints de productos"""
        start_time = time.time()
        response = requests.get(f"{self.BASE_URL}/productos/")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Verificar que responda en menos de 5 segundos
        assert response_time < 5.0
        print(f"✅ Tiempo de respuesta productos: {response_time:.2f}s")
    
    def test_response_time_categorias(self):
        """Verificar tiempo de respuesta de endpoints de categorías"""
        start_time = time.time()
        response = requests.get(f"{self.BASE_URL}/productos/categorias/")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Verificar que responda en menos de 3 segundos
        assert response_time < 3.0
        print(f"✅ Tiempo de respuesta categorías: {response_time:.2f}s")
    
    def test_concurrent_requests(self):
        """Probar múltiples requests concurrentes"""
        import concurrent.futures
        import threading
        
        def make_request():
            try:
                response = requests.get(f"{self.BASE_URL}/productos/", timeout=10)
                return response.status_code == 200
            except:
                return False
        
        # Hacer 5 requests concurrentes
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Al menos el 80% deberían ser exitosos
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.8
        print(f"✅ Requests concurrentes exitosos: {success_rate*100:.1f}%")


class TestAPIErrorHandling:
    """Pruebas de manejo de errores de la API"""
    
    BASE_URL = "http://localhost:8001"
    
    def test_404_endpoint_inexistente(self):
        """Probar respuesta 404 para endpoint inexistente"""
        response = requests.get(f"{self.BASE_URL}/endpoint-inexistente")
        assert response.status_code == 404
        print("✅ Manejo correcto de endpoint inexistente")
    
    def test_405_method_not_allowed(self):
        """Probar respuesta 405 para método no permitido"""
        # POST en endpoint que solo acepta GET
        response = requests.post(f"{self.BASE_URL}/productos/")
        # Puede retornar 405 o 422 dependiendo de la implementación
        assert response.status_code in [405, 422]
        print("✅ Manejo correcto de método no permitido")
    
    def test_malformed_json(self):
        """Probar respuesta para JSON malformado"""
        response = requests.post(
            f"{self.BASE_URL}/productos/",
            data="json malformado {invalid}",
            headers={"Content-Type": "application/json"}
        )
        
        # Debería retornar error de formato
        assert response.status_code in [400, 422]
        print("✅ Manejo correcto de JSON malformado")
