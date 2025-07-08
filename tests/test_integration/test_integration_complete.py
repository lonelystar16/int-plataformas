"""
Pruebas de Integración para FerramasStore
Basado en el Plan de Pruebas de Integración generado
"""

import pytest
import requests
import json
from unittest.mock import patch, MagicMock
from utils.base_test import BaseTest
from utils.api_helpers import APIHelper


class TestIntegracionBancoCentral(BaseTest):
    """INT-001: Integración Banco Central - Obtener Cotizaciones"""
    
    def test_obtener_cotizaciones_banco_central(self):
        """
        Verificar que el sistema pueda obtener cotizaciones del Banco Central correctamente
        """
        # Precondiciones
        assert self.check_internet_connection(), "Conexión a internet requerida"
        
        # Pasos de ejecución
        api_helper = APIHelper()
        
        # 1. Realizar petición GET a la API
        response = api_helper.get('/api/banco-central/cotizaciones')
        
        # 2. Verificar respuesta exitosa
        assert response.status_code == 200, f"Error en respuesta: {response.status_code}"
        
        # 3. Validar formato de datos
        data = response.json()
        assert isinstance(data, dict), "Respuesta debe ser un objeto JSON"
        assert 'cotizaciones' in data, "Debe contener campo 'cotizaciones'"
        
        # Resultado esperado
        cotizaciones = data['cotizaciones']
        assert len(cotizaciones) > 0, "Debe haber al menos una cotización"
        
        # Validar estructura de cotización
        for cotizacion in cotizaciones:
            assert 'moneda' in cotizacion, "Cada cotización debe tener 'moneda'"
            assert 'valor' in cotizacion, "Cada cotización debe tener 'valor'"
            assert isinstance(cotizacion['valor'], (int, float)), "Valor debe ser numérico"
    
    def test_manejo_error_banco_central_no_disponible(self):
        """
        Verificar manejo de errores cuando API del Banco Central no está disponible
        """
        api_helper = APIHelper()
        
        with patch('requests.get') as mock_get:
            # Simular API no disponible
            mock_get.side_effect = requests.exceptions.ConnectionError("API no disponible")
            
            # Verificar que el sistema maneja el error gracefully
            response = api_helper.get('/api/banco-central/cotizaciones')
            
            # El sistema debe devolver un error controlado, no crash
            assert response is not None, "Sistema debe manejar errores de conexión"


class TestIntegracionMercadoPago(BaseTest):
    """INT-002: Integración MercadoPago - Procesar Pago"""
    
    @pytest.fixture
    def producto_en_carrito(self):
        """Precondición: producto en carrito"""
        return {
            'id': 1,
            'nombre': 'Producto Test',
            'precio': 100.0,
            'cantidad': 1
        }
    
    def test_procesar_pago_mercadopago(self, producto_en_carrito):
        """
        Verificar procesamiento de pagos a través de MercadoPago
        """
        api_helper = APIHelper()
        
        # Precondiciones
        assert 'MERCADOPAGO_ACCESS_TOKEN' in os.environ, "Token de MercadoPago requerido"
        
        # Datos de pago
        payment_data = {
            'transaction_amount': producto_en_carrito['precio'],
            'description': producto_en_carrito['nombre'],
            'payment_method_id': 'visa',
            'payer': {
                'email': 'test@example.com'
            }
        }
        
        # 1. Iniciar proceso de pago
        response = api_helper.post('/api/mercado-pago/payments', data=payment_data)
        
        # 2. Verificar respuesta de MercadoPago
        assert response.status_code in [200, 201], f"Error en pago: {response.status_code}"
        
        payment_result = response.json()
        
        # 3. Verificar confirmación
        assert 'id' in payment_result, "Debe tener ID de transacción"
        assert 'status' in payment_result, "Debe tener status de pago"
        
        # 4. Verificar actualización de estado del pedido
        payment_id = payment_result['id']
        order_response = api_helper.get(f'/api/orders/by-payment/{payment_id}')
        
        assert order_response.status_code == 200, "Debe encontrar orden asociada"
        order = order_response.json()
        assert order['status'] in ['paid', 'confirmed'], "Orden debe estar confirmada"


class TestIntegracionAPIProductos(BaseTest):
    """INT-003: Integración API Productos - CRUD Completo"""
    
    def test_crud_completo_productos(self):
        """
        Verificar operaciones CRUD en la API de productos
        """
        api_helper = APIHelper()
        
        # Precondiciones
        self.authenticate_user()  # Usuario autenticado
        
        # 1. Crear producto
        nuevo_producto = {
            'nombre': 'Producto Test CRUD',
            'descripcion': 'Producto para testing',
            'precio': 99.99,
            'categoria': 'test'
        }
        
        create_response = api_helper.post('/api/productos/', data=nuevo_producto)
        assert create_response.status_code == 201, "Error al crear producto"
        
        producto_creado = create_response.json()
        producto_id = producto_creado['id']
        
        # 2. Leer producto
        read_response = api_helper.get(f'/api/productos/{producto_id}')
        assert read_response.status_code == 200, "Error al leer producto"
        
        producto_leido = read_response.json()
        assert producto_leido['nombre'] == nuevo_producto['nombre']
        
        # 3. Actualizar producto
        producto_actualizado = {
            'nombre': 'Producto Test CRUD Actualizado',
            'precio': 149.99
        }
        
        update_response = api_helper.put(f'/api/productos/{producto_id}', data=producto_actualizado)
        assert update_response.status_code == 200, "Error al actualizar producto"
        
        # Verificar actualización
        verify_response = api_helper.get(f'/api/productos/{producto_id}')
        producto_verificado = verify_response.json()
        assert producto_verificado['precio'] == 149.99
        
        # 4. Eliminar producto
        delete_response = api_helper.delete(f'/api/productos/{producto_id}')
        assert delete_response.status_code in [200, 204], "Error al eliminar producto"
        
        # Verificar eliminación
        final_response = api_helper.get(f'/api/productos/{producto_id}')
        assert final_response.status_code == 404, "Producto debe estar eliminado"


class TestFlujoCompletoEcommerce(BaseTest):
    """INT-004: Flujo Completo E-commerce"""
    
    def test_flujo_completo_compra(self):
        """
        Prueba de integración del flujo completo de compra
        """
        api_helper = APIHelper()
        
        # Precondiciones: todas las APIs funcionando
        self.verify_all_services_available()
        
        # 1. Autenticar usuario
        auth_data = {'username': 'testuser', 'password': 'testpass'}
        auth_response = api_helper.post('/api/auth/login', data=auth_data)
        assert auth_response.status_code == 200, "Error en autenticación"
        
        token = auth_response.json()['token']
        api_helper.set_auth_token(token)
        
        # 2. Buscar productos
        products_response = api_helper.get('/api/productos/')
        assert products_response.status_code == 200, "Error al obtener productos"
        
        productos = products_response.json()
        assert len(productos) > 0, "Debe haber productos disponibles"
        
        # 3. Agregar al carrito
        producto = productos[0]
        cart_data = {'producto_id': producto['id'], 'cantidad': 1}
        cart_response = api_helper.post('/api/carrito/agregar', data=cart_data)
        assert cart_response.status_code == 200, "Error al agregar al carrito"
        
        # 4. Obtener cotización
        cotiz_response = api_helper.get('/api/banco-central/cotizaciones')
        assert cotiz_response.status_code == 200, "Error al obtener cotización"
        
        # 5. Procesar pago
        payment_data = {
            'amount': producto['precio'],
            'currency': 'USD'
        }
        payment_response = api_helper.post('/api/mercado-pago/payments', data=payment_data)
        assert payment_response.status_code in [200, 201], "Error en procesamiento de pago"
        
        # 6. Confirmar pedido
        order_data = {'payment_id': payment_response.json()['id']}
        order_response = api_helper.post('/api/orders/confirmar', data=order_data)
        assert order_response.status_code == 201, "Error al confirmar pedido"
        
        # Verificar estado final
        order = order_response.json()
        assert order['status'] == 'confirmed', "Pedido debe estar confirmado"
    
    def verify_all_services_available(self):
        """Verificar que todos los servicios estén disponibles"""
        api_helper = APIHelper()
        
        # Verificar API productos
        assert api_helper.get('/api/productos/').status_code == 200
        
        # Verificar API banco central
        assert api_helper.get('/api/banco-central/cotizaciones').status_code == 200
        
        # Verificar API auth
        assert api_helper.get('/api/auth/status').status_code == 200


class TestManejoErrores(BaseTest):
    """INT-005: Manejo de Errores - APIs Externas"""
    
    def test_manejo_errores_apis_externas(self):
        """
        Verificar manejo de errores cuando APIs externas no están disponibles
        """
        api_helper = APIHelper()
        
        with patch('requests.get') as mock_get:
            # Simular APIs externas no disponibles
            mock_get.side_effect = requests.exceptions.Timeout("Timeout")
            
            # 1. Intentar conectar a API no disponible
            response = api_helper.get('/api/banco-central/cotizaciones')
            
            # 2. Verificar mensaje de error apropiado
            assert response is not None, "Debe retornar respuesta de error"
            
            if hasattr(response, 'json'):
                error_data = response.json()
                assert 'error' in error_data, "Debe incluir mensaje de error"
            
            # 3. Confirmar que el resto del sistema sigue funcionando
            # APIs internas deben seguir funcionando
            products_response = api_helper.get('/api/productos/')
            assert products_response.status_code == 200, "APIs internas deben seguir funcionando"


class TestAutenticacionAutorizacion(BaseTest):
    """INT-006: Autenticación y Autorización"""
    
    def test_sistema_autenticacion_completo(self):
        """
        Verificar sistema de autenticación integrado
        """
        api_helper = APIHelper()
        
        # 1. Intentar login con credenciales válidas
        valid_credentials = {'username': 'testuser', 'password': 'testpass'}
        login_response = api_helper.post('/api/auth/login', data=valid_credentials)
        
        assert login_response.status_code == 200, "Login debe ser exitoso"
        
        # 2. Verificar tokens de sesión
        auth_data = login_response.json()
        assert 'token' in auth_data, "Debe retornar token de acceso"
        
        token = auth_data['token']
        api_helper.set_auth_token(token)
        
        # 3. Probar acceso a recursos protegidos
        protected_response = api_helper.get('/api/admin/users')
        assert protected_response.status_code in [200, 403], "Debe permitir o denegar acceso"
        
        # 4. Verificar logout
        logout_response = api_helper.post('/api/auth/logout')
        assert logout_response.status_code == 200, "Logout debe ser exitoso"
        
        # Verificar que token ya no es válido
        api_helper.set_auth_token(token)
        verify_response = api_helper.get('/api/auth/verify')
        assert verify_response.status_code == 401, "Token debe estar invalidado"


if __name__ == "__main__":
    # Ejecutar pruebas específicas
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--html=reports/integration_test_report.html'
    ])
