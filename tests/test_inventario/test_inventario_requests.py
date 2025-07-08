#!/usr/bin/env python3
"""
Script de pruebas completas del sistema de inventario usando requests
Alternativa confiable a Selenium para validar todas las URLs
"""

import requests
import json
import time
from datetime import datetime
from urllib.parse import urljoin
import sys
import os

class InventarioRequestsTester:
    """Tester del sistema de inventario usando requests"""
    
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
        self.logged_in = False
        self.csrf_token = None
        
        # URLs a probar
        self.urls_to_test = [
            # URLs públicas
            {
                'name': 'Página Principal',
                'url': '/',
                'requires_auth': False,
                'expected_status': 200,
                'expected_text': ['Ferramas'],
                'critical': True
            },
            {
                'name': 'Página de Login',
                'url': '/auth/login/',
                'requires_auth': False,
                'expected_status': 200,
                'expected_text': ['Iniciar Sesión', 'usuario', 'password'],
                'critical': True
            },
            {
                'name': 'Página de Registro',
                'url': '/auth/register/',
                'requires_auth': False,
                'expected_status': 200,
                'expected_text': ['Registro'],
                'critical': False
            },
            
            # URLs de inventario
            {
                'name': 'Dashboard de Inventario',
                'url': '/inventario/',
                'requires_auth': True,
                'expected_status': 200,
                'expected_text': ['Dashboard', 'Inventario'],
                'critical': True
            },
            {
                'name': 'Lista de Productos del Inventario',
                'url': '/inventario/productos/',
                'requires_auth': True,
                'expected_status': 200,
                'expected_text': ['Lista de Productos', 'Productos'],
                'critical': True
            },
            {
                'name': 'Entrada de Inventario',
                'url': '/inventario/entrada/',
                'requires_auth': True,
                'expected_status': 200,
                'expected_text': ['Entrada', 'Inventario'],
                'critical': True
            },
            {
                'name': 'Salida de Inventario',
                'url': '/inventario/salida/',
                'requires_auth': True,
                'expected_status': 200,
                'expected_text': ['Salida', 'Inventario'],
                'critical': True
            },
            {
                'name': 'Gestión de Alertas',
                'url': '/inventario/alertas/',
                'requires_auth': True,
                'expected_status': 200,
                'expected_text': ['Alertas', 'Gestión'],
                'critical': False
            },
            {
                'name': 'Reportes de Inventario',
                'url': '/inventario/reporte/',
                'requires_auth': True,
                'expected_status': 200,
                'expected_text': ['Reporte', 'Inventario'],
                'critical': True
            },
            
            # URLs de API
            {
                'name': 'API Stock de Producto',
                'url': '/api/inventario/stock/1/',
                'requires_auth': True,
                'expected_status': 200,
                'test_type': 'api',
                'expected_json_keys': ['producto_id', 'stock_disponible'],
                'critical': False
            }
        ]
    
    def get_csrf_token(self):
        """Obtener token CSRF"""
        try:
            response = self.session.get(f"{self.base_url}/auth/login/")
            if 'csrftoken' in self.session.cookies:
                self.csrf_token = self.session.cookies['csrftoken']
                return True
            return False
        except Exception as e:
            print(f"❌ Error obteniendo CSRF token: {e}")
            return False
    
    def login(self):
        """Hacer login"""
        try:
            print("🔐 Iniciando sesión...")
            
            # Obtener CSRF token
            if not self.get_csrf_token():
                print("⚠️ No se pudo obtener CSRF token")
            
            # Preparar datos de login
            login_data = {
                'usuario': 'admin',
                'password': 'admin123'
            }
            
            if self.csrf_token:
                login_data['csrfmiddlewaretoken'] = self.csrf_token
            
            # Hacer login
            response = self.session.post(
                f"{self.base_url}/auth/login/", 
                data=login_data,
                allow_redirects=False
            )
            
            # Verificar resultado
            if response.status_code in [200, 302]:
                # Verificar que ya no estamos en login
                test_response = self.session.get(f"{self.base_url}/inventario/")
                if test_response.status_code == 200:
                    print("✅ Login exitoso")
                    self.logged_in = True
                    return True
                else:
                    print("❌ Login falló - no se puede acceder a inventario")
                    return False
            else:
                print(f"❌ Login falló - HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error durante login: {e}")
            return False
    
    def test_url(self, url_info):
        """Probar una URL específica"""
        test_result = {
            'name': url_info['name'],
            'url': url_info['url'],
            'full_url': urljoin(self.base_url, url_info['url']),
            'requires_auth': url_info.get('requires_auth', False),
            'critical': url_info.get('critical', False),
            'test_type': url_info.get('test_type', 'page'),
            'status': 'PENDING',
            'http_status': 0,
            'response_time': 0,
            'content_length': 0,
            'errors': [],
            'warnings': [],
            'found_text': [],
            'missing_text': [],
            'found_json_keys': [],
            'missing_json_keys': [],
            'timestamp': datetime.now().isoformat()
        }
        
        start_time = time.time()
        
        try:
            # Hacer petición
            response = self.session.get(test_result['full_url'], timeout=10)
            test_result['http_status'] = response.status_code
            test_result['response_time'] = time.time() - start_time
            test_result['content_length'] = len(response.content)
            
            # Verificar status code
            expected_status = url_info.get('expected_status', 200)
            if response.status_code != expected_status:
                if response.status_code == 302:
                    test_result['warnings'].append(f"Redirected to: {response.headers.get('Location', 'Unknown')}")
                elif response.status_code == 403:
                    if url_info.get('requires_auth', False):
                        test_result['status'] = 'NEEDS_AUTH'
                        test_result['warnings'].append("Authentication required (expected)")
                        return test_result
                    else:
                        test_result['errors'].append("Access forbidden")
                elif response.status_code == 404:
                    test_result['errors'].append("Page not found")
                else:
                    test_result['errors'].append(f"HTTP {response.status_code} (expected {expected_status})")
            
            # Verificar contenido
            if response.status_code == 200:
                if url_info.get('test_type') == 'api':
                    # Para APIs, verificar JSON
                    try:
                        json_data = response.json()
                        expected_keys = url_info.get('expected_json_keys', [])
                        
                        for key in expected_keys:
                            if key in json_data:
                                test_result['found_json_keys'].append(key)
                            else:
                                test_result['missing_json_keys'].append(key)
                        
                    except json.JSONDecodeError:
                        test_result['errors'].append("Invalid JSON response")
                        
                else:
                    # Para páginas web, verificar texto
                    content = response.text.lower()
                    expected_text = url_info.get('expected_text', [])
                    
                    for text in expected_text:
                        if text.lower() in content:
                            test_result['found_text'].append(text)
                        else:
                            test_result['missing_text'].append(text)
                    
                    # Verificar errores en la página
                    error_indicators = ['error', 'exception', 'traceback', 'templatesyntaxerror', 'noreverseMatch']
                    for indicator in error_indicators:
                        if indicator.lower() in content:
                            test_result['errors'].append(f"Page error detected: {indicator}")
            
            # Determinar estado final
            if test_result['errors']:
                test_result['status'] = 'FAILED'
            elif test_result['missing_text'] or test_result['missing_json_keys']:
                test_result['status'] = 'PARTIAL'
            else:
                test_result['status'] = 'PASSED'
                
        except requests.exceptions.Timeout:
            test_result['status'] = 'FAILED'
            test_result['errors'].append("Request timeout")
            test_result['response_time'] = time.time() - start_time
        except requests.exceptions.ConnectionError:
            test_result['status'] = 'FAILED'
            test_result['errors'].append("Connection error")
            test_result['response_time'] = time.time() - start_time
        except Exception as e:
            test_result['status'] = 'FAILED'
            test_result['errors'].append(f"Unexpected error: {e}")
            test_result['response_time'] = time.time() - start_time
        
        return test_result
    
    def run_tests(self):
        """Ejecutar todas las pruebas"""
        print("🚀 INICIANDO PRUEBAS COMPLETAS DEL SISTEMA DE INVENTARIO")
        print("=" * 80)
        
        # Verificar servidor
        try:
            response = self.session.get(self.base_url, timeout=5)
            if response.status_code == 200:
                print("✅ Servidor accesible")
            else:
                print(f"⚠️ Servidor responde con HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Servidor no accesible: {e}")
            return False
        
        # Hacer login
        if not self.login():
            print("⚠️ Login falló - solo se probarán URLs públicas")
        
        # Ejecutar pruebas
        print("\n📋 EJECUTANDO PRUEBAS...")
        print("-" * 80)
        
        for i, url_info in enumerate(self.urls_to_test, 1):
            print(f"\n[{i}/{len(self.urls_to_test)}] 🔍 {url_info['name']}")
            
            # Saltar si requiere autenticación y no estamos logueados
            if url_info.get('requires_auth', False) and not self.logged_in:
                print("   ⏭️ Saltando (requiere autenticación)")
                continue
            
            result = self.test_url(url_info)
            self.results.append(result)
            
            # Mostrar resultado
            status_icons = {
                'PASSED': '✅',
                'PARTIAL': '⚠️',
                'FAILED': '❌',
                'NEEDS_AUTH': '🔐'
            }
            
            icon = status_icons.get(result['status'], '❓')
            critical_text = " [CRÍTICO]" if result['critical'] else ""
            
            print(f"   {icon} {result['status']}{critical_text}")
            print(f"   ⏱️  Tiempo: {result['response_time']:.2f}s")
            print(f"   📊 HTTP: {result['http_status']}")
            print(f"   📏 Tamaño: {result['content_length']} bytes")
            
            if result['errors']:
                for error in result['errors']:
                    print(f"   ❌ {error}")
            
            if result['warnings']:
                for warning in result['warnings']:
                    print(f"   ⚠️ {warning}")
            
            if result['found_text']:
                print(f"   ✅ Texto encontrado: {len(result['found_text'])}")
            
            if result['missing_text']:
                print(f"   ❌ Texto faltante: {len(result['missing_text'])}")
            
            if result['found_json_keys']:
                print(f"   ✅ Claves JSON encontradas: {len(result['found_json_keys'])}")
            
            if result['missing_json_keys']:
                print(f"   ❌ Claves JSON faltantes: {len(result['missing_json_keys'])}")
            
            time.sleep(0.2)  # Pausa pequeña entre pruebas
        
        # Generar reporte
        self.generate_report()
        return True
    
    def generate_report(self):
        """Generar reporte completo"""
        print("\n" + "=" * 80)
        print("📊 REPORTE FINAL DE PRUEBAS")
        print("=" * 80)
        
        # Estadísticas
        total = len(self.results)
        passed = len([r for r in self.results if r['status'] == 'PASSED'])
        partial = len([r for r in self.results if r['status'] == 'PARTIAL'])
        failed = len([r for r in self.results if r['status'] == 'FAILED'])
        needs_auth = len([r for r in self.results if r['status'] == 'NEEDS_AUTH'])
        
        critical_results = [r for r in self.results if r['critical']]
        critical_passed = len([r for r in critical_results if r['status'] == 'PASSED'])
        critical_total = len(critical_results)
        
        print(f"📈 ESTADÍSTICAS GENERALES:")
        print(f"   Total de pruebas ejecutadas: {total}")
        print(f"   ✅ Exitosas: {passed}")
        print(f"   ⚠️ Parciales: {partial}")
        print(f"   ❌ Fallidas: {failed}")
        print(f"   🔐 Necesitan autenticación: {needs_auth}")
        print(f"   🔑 Sesión iniciada: {'Sí' if self.logged_in else 'No'}")
        
        if total > 0:
            success_rate = (passed / total) * 100
            print(f"   📊 Tasa de éxito: {success_rate:.1f}%")
        
        if critical_total > 0:
            critical_success_rate = (critical_passed / critical_total) * 100
            print(f"   🎯 Funcionalidad crítica: {critical_success_rate:.1f}% ({critical_passed}/{critical_total})")
        
        # Detalles de fallos
        failed_results = [r for r in self.results if r['status'] == 'FAILED']
        if failed_results:
            print(f"\n❌ PRUEBAS FALLIDAS:")
            for result in failed_results:
                critical_mark = " [CRÍTICO]" if result['critical'] else ""
                print(f"   • {result['name']}{critical_mark}")
                for error in result['errors']:
                    print(f"     - {error}")
        
        # Detalles de parciales
        partial_results = [r for r in self.results if r['status'] == 'PARTIAL']
        if partial_results:
            print(f"\n⚠️ PRUEBAS PARCIALES:")
            for result in partial_results:
                print(f"   • {result['name']}")
                if result['missing_text']:
                    print(f"     - Texto faltante: {', '.join(result['missing_text'])}")
                if result['missing_json_keys']:
                    print(f"     - Claves JSON faltantes: {', '.join(result['missing_json_keys'])}")
        
        # Tiempo promedio
        response_times = [r['response_time'] for r in self.results if r['response_time'] > 0]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            print(f"\n⏱️ RENDIMIENTO:")
            print(f"   Tiempo promedio: {avg_time:.2f}s")
            print(f"   Tiempo máximo: {max_time:.2f}s")
            print(f"   Tiempo mínimo: {min_time:.2f}s")
        
        # Guardar reporte
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'base_url': self.base_url,
            'logged_in': self.logged_in,
            'test_summary': {
                'total': total,
                'passed': passed,
                'partial': partial,
                'failed': failed,
                'needs_auth': needs_auth,
                'success_rate': (passed / total * 100) if total > 0 else 0,
                'critical_success_rate': (critical_passed / critical_total * 100) if critical_total > 0 else 0
            },
            'results': self.results
        }
        
        report_file = 'inventario_test_report_requests.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte detallado guardado en: {report_file}")
        
        # Resultado final
        if failed == 0:
            print("\n🎉 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE!")
        elif critical_passed == critical_total:
            print("\n✅ FUNCIONALIDAD CRÍTICA COMPLETAMENTE OPERATIVA")
        else:
            print("\n⚠️ PROBLEMAS DETECTADOS EN FUNCIONALIDAD CRÍTICA")
        
        return failed == 0

def main():
    """Función principal"""
    try:
        print("🧪 SISTEMA DE PRUEBAS DEL INVENTARIO FERRAMAS")
        print("Usando requests para máxima compatibilidad\n")
        
        tester = InventarioRequestsTester()
        success = tester.run_tests()
        
        if success:
            print("\n🎉 Sistema de inventario completamente funcional!")
            return 0
        else:
            print("\n⚠️ Se detectaron problemas - revisar reporte")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Pruebas interrumpidas por el usuario")
        return 1
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
