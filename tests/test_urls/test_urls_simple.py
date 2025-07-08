#!/usr/bin/env python3
"""
Script simplificado de pruebas de URLs usando requests
Como alternativa a Selenium si hay problemas con el driver
"""

import requests
import json
from datetime import datetime
import os
import sys

class SimpleURLTester:
    """Clase para probar URLs usando requests"""
    
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
        
        # URLs a probar
        self.urls_to_test = [
            # URLs públicas
            {'name': 'Página Principal', 'url': '/', 'requires_auth': False},
            {'name': 'Página de Login', 'url': '/auth/login/', 'requires_auth': False},
            {'name': 'Página de Registro', 'url': '/auth/register/', 'requires_auth': False},
            
            # URLs de inventario (requieren autenticación)
            {'name': 'Dashboard de Inventario', 'url': '/inventario/', 'requires_auth': True},
            {'name': 'Lista de Productos', 'url': '/inventario/productos/', 'requires_auth': True},
            {'name': 'Entrada de Inventario', 'url': '/inventario/entrada/', 'requires_auth': True},
            {'name': 'Salida de Inventario', 'url': '/inventario/salida/', 'requires_auth': True},
            {'name': 'Gestión de Alertas', 'url': '/inventario/alertas/', 'requires_auth': True},
            {'name': 'Reportes de Inventario', 'url': '/inventario/reporte/', 'requires_auth': True},
            
            # API endpoints
            {'name': 'API Status', 'url': '/api/', 'requires_auth': False, 'is_api': True},
            {'name': 'API Stock Producto', 'url': '/api/inventario/stock/1/', 'requires_auth': True, 'is_api': True},
        ]
    
    def login(self):
        """Intentar hacer login"""
        try:
            # Obtener el formulario de login
            login_url = f"{self.base_url}/auth/login/"
            response = self.session.get(login_url)
            
            if response.status_code != 200:
                print(f"❌ Error accediendo a login: {response.status_code}")
                return False
            
            # Extraer CSRF token si existe
            csrf_token = None
            if 'csrftoken' in self.session.cookies:
                csrf_token = self.session.cookies['csrftoken']
            
            # Intentar login
            login_data = {
                'username': 'admin',
                'password': 'admin123',
            }
            
            if csrf_token:
                login_data['csrfmiddlewaretoken'] = csrf_token
            
            response = self.session.post(login_url, data=login_data)
            
            # Verificar si el login fue exitoso
            if response.status_code == 200 and '/auth/login/' not in response.url:
                print("✅ Login exitoso")
                return True
            elif response.status_code == 302:
                print("✅ Login exitoso (redirección)")
                return True
            else:
                print(f"❌ Login falló: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error durante login: {e}")
            return False
    
    def test_url(self, url_info):
        """Probar una URL específica"""
        test_result = {
            'name': url_info['name'],
            'url': url_info['url'],
            'full_url': f"{self.base_url}{url_info['url']}",
            'status': 'PENDING',
            'http_status': 0,
            'response_time': 0,
            'errors': [],
            'warnings': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            import time
            start_time = time.time()
            
            response = self.session.get(test_result['full_url'], timeout=10)
            test_result['response_time'] = time.time() - start_time
            test_result['http_status'] = response.status_code
            
            # Evaluar respuesta
            if response.status_code == 200:
                if url_info.get('is_api', False):
                    # Para APIs, verificar JSON
                    try:
                        json_data = response.json()
                        test_result['status'] = 'PASSED'
                        test_result['warnings'].append(f"JSON response: {len(json_data)} items")
                    except:
                        test_result['status'] = 'PASSED'
                        test_result['warnings'].append("Non-JSON response")
                else:
                    # Para páginas HTML
                    content = response.text.lower()
                    if 'error' in content or 'exception' in content:
                        test_result['status'] = 'WARNING'
                        test_result['warnings'].append("Page contains error keywords")
                    else:
                        test_result['status'] = 'PASSED'
                        
            elif response.status_code == 302:
                test_result['status'] = 'PASSED'
                test_result['warnings'].append(f"Redirect to: {response.headers.get('Location', 'Unknown')}")
                
            elif response.status_code == 403:
                if url_info.get('requires_auth', False):
                    test_result['status'] = 'EXPECTED'
                    test_result['warnings'].append("Authentication required (expected)")
                else:
                    test_result['status'] = 'FAILED'
                    test_result['errors'].append("Access forbidden")
                    
            elif response.status_code == 404:
                test_result['status'] = 'FAILED'
                test_result['errors'].append("Page not found")
                
            else:
                test_result['status'] = 'FAILED'
                test_result['errors'].append(f"HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            test_result['status'] = 'FAILED'
            test_result['errors'].append("Request timeout")
            
        except requests.exceptions.ConnectionError:
            test_result['status'] = 'FAILED'
            test_result['errors'].append("Connection error")
            
        except Exception as e:
            test_result['status'] = 'FAILED'
            test_result['errors'].append(f"Unexpected error: {e}")
        
        return test_result
    
    def run_tests(self):
        """Ejecutar todas las pruebas"""
        print("🚀 Iniciando pruebas simples de URLs...")
        print("=" * 60)
        
        # Intentar login
        login_success = self.login()
        
        # Probar todas las URLs
        for url_info in self.urls_to_test:
            print(f"\n🔍 Probando: {url_info['name']}")
            
            result = self.test_url(url_info)
            self.results.append(result)
            
            # Mostrar resultado
            status_icon = {
                'PASSED': '✅',
                'WARNING': '⚠️',
                'FAILED': '❌',
                'EXPECTED': '🔐'
            }.get(result['status'], '❓')
            
            print(f"   {status_icon} {result['status']} - HTTP {result['http_status']} - {result['response_time']:.2f}s")
            
            if result['errors']:
                for error in result['errors']:
                    print(f"      ❌ {error}")
            
            if result['warnings']:
                for warning in result['warnings']:
                    print(f"      ⚠️ {warning}")
        
        # Generar reporte
        self.generate_report()
    
    def generate_report(self):
        """Generar reporte de resultados"""
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE RESULTADOS")
        print("=" * 60)
        
        passed = len([r for r in self.results if r['status'] == 'PASSED'])
        failed = len([r for r in self.results if r['status'] == 'FAILED'])
        warnings = len([r for r in self.results if r['status'] == 'WARNING'])
        expected = len([r for r in self.results if r['status'] == 'EXPECTED'])
        
        print(f"✅ Pasadas: {passed}")
        print(f"❌ Fallidas: {failed}")
        print(f"⚠️ Advertencias: {warnings}")
        print(f"🔐 Esperadas: {expected}")
        print(f"📊 Total: {len(self.results)}")
        
        # Guardar reporte en archivo
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'passed': passed,
                'failed': failed,
                'warnings': warnings,
                'expected': expected,
                'total': len(self.results)
            },
            'results': self.results
        }
        
        with open('test_report_simple.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte guardado en: test_report_simple.json")
        
        if failed > 0:
            print("\n❌ Algunas pruebas fallaron. Revisar el reporte para detalles.")
            return False
        else:
            print("\n✅ Todas las pruebas pasaron o son esperadas.")
            return True

def main():
    """Función principal"""
    try:
        tester = SimpleURLTester()
        success = tester.run_tests()
        
        if success:
            print("\n🎉 Pruebas completadas exitosamente!")
        else:
            print("\n💥 Algunas pruebas fallaron.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")

if __name__ == "__main__":
    main()
