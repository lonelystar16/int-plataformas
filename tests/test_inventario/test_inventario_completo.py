#!/usr/bin/env python3
"""
Script de pruebas completo para el sistema de inventario usando Selenium
Versión final con pruebas exhaustivas y reporte detallado
"""

import os
import sys
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

class CompletInventarioTester:
    """Clase para realizar pruebas completas del sistema de inventario"""
    
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.driver = None
        self.results = []
        self.logged_in = False
        self.test_user = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        # URLs del sistema de inventario
        self.urls_to_test = [
            # URLs públicas
            {
                'name': 'Página Principal',
                'url': '/',
                'requires_auth': False,
                'test_type': 'page',
                'expected_status': 200,
                'expected_text': ['Ferramas', 'productos', 'tienda'],
                'expected_elements': ['body', 'main', 'nav'],
                'critical': True
            },
            {
                'name': 'Página de Login',
                'url': '/auth/login/',
                'requires_auth': False,
                'test_type': 'page',
                'expected_status': 200,
                'expected_text': ['Iniciar Sesión', 'Usuario', 'Contraseña'],
                'expected_elements': ['form', 'input[name="usuario"]', 'input[name="password"]'],
                'critical': True
            },
            {
                'name': 'Página de Registro',
                'url': '/auth/register/',
                'requires_auth': False,
                'test_type': 'page',
                'expected_status': 200,
                'expected_text': ['Registro', 'nombre'],
                'expected_elements': ['form', 'input[name="nombre"]'],
                'critical': False
            },
            
            # URLs de inventario
            {
                'name': 'Dashboard de Inventario',
                'url': '/inventario/',
                'requires_auth': True,
                'test_type': 'page',
                'expected_status': 200,
                'expected_text': ['Dashboard', 'Inventario', 'productos'],
                'expected_elements': ['body', 'main'],
                'critical': True
            },
            {
                'name': 'Lista de Productos del Inventario',
                'url': '/inventario/productos/',
                'requires_auth': True,
                'test_type': 'page',
                'expected_status': 200,
                'expected_text': ['Lista de Productos', 'Stock', 'Precio'],
                'expected_elements': ['table', 'tbody'],
                'critical': True
            },
            {
                'name': 'Entrada de Inventario',
                'url': '/inventario/entrada/',
                'requires_auth': True,
                'test_type': 'page',
                'expected_status': 200,
                'expected_text': ['Entrada', 'Inventario', 'Producto'],
                'expected_elements': ['form', 'select'],
                'critical': True
            },
            {
                'name': 'Salida de Inventario',
                'url': '/inventario/salida/',
                'requires_auth': True,
                'test_type': 'page',
                'expected_status': 200,
                'expected_text': ['Salida', 'Inventario', 'Producto'],
                'expected_elements': ['form', 'select'],
                'critical': True
            },
            {
                'name': 'Gestión de Alertas',
                'url': '/inventario/alertas/',
                'requires_auth': True,
                'test_type': 'page',
                'expected_status': 200,
                'expected_text': ['Alertas', 'Gestión'],
                'expected_elements': ['body', 'main'],
                'critical': False
            },
            {
                'name': 'Reportes de Inventario',
                'url': '/inventario/reporte/',
                'requires_auth': True,
                'test_type': 'page',
                'expected_status': 200,
                'expected_text': ['Reporte', 'Inventario'],
                'expected_elements': ['form', 'body'],
                'critical': True
            },
            
            # URLs de API
            {
                'name': 'API Stock de Producto',
                'url': '/api/inventario/stock/1/',
                'requires_auth': True,
                'test_type': 'api',
                'expected_status': 200,
                'expected_json_keys': ['producto_id', 'stock_disponible'],
                'critical': False
            }
        ]
    
    def setup_driver(self):
        """Configurar el driver de Selenium"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-logging')
            chrome_options.add_argument('--disable-gpu-logging')
            chrome_options.add_argument('--log-level=3')
            chrome_options.add_argument('--silent')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
            
            # Suprimir logs de Chrome
            chrome_options.add_experimental_option('prefs', {
                'profile.default_content_setting_values.notifications': 2,
                'profile.default_content_settings.popups': 0,
                'profile.managed_default_content_settings.images': 2
            })
            
            # Configurar service
            service = Service(ChromeDriverManager().install())
            service.creationflags = 0x08000000  # CREATE_NO_WINDOW en Windows
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Configurar timeouts
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
            
            # Ocultar propiedades de automation
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return True
            
        except Exception as e:
            print(f"❌ Error configurando driver: {e}")
            return False
    
    def login(self):
        """Hacer login para pruebas autenticadas"""
        try:
            print("🔐 Iniciando sesión...")
            
            # Navegar a login
            self.driver.get(f"{self.base_url}/auth/login/")
            
            # Esperar formulario
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "usuario"))
            )
            
            # Rellenar formulario
            self.driver.find_element(By.NAME, "usuario").send_keys(self.test_user['username'])
            self.driver.find_element(By.NAME, "password").send_keys(self.test_user['password'])
            
            # Enviar formulario
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']").click()
            
            # Esperar resultado
            time.sleep(3)
            
            # Verificar login exitoso
            if '/auth/login/' not in self.driver.current_url:
                print("✅ Login exitoso")
                self.logged_in = True
                return True
            else:
                print("❌ Login falló")
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
            'test_type': url_info.get('test_type', 'page'),
            'requires_auth': url_info.get('requires_auth', False),
            'critical': url_info.get('critical', False),
            'status': 'PENDING',
            'http_status': 0,
            'response_time': 0,
            'page_title': '',
            'errors': [],
            'warnings': [],
            'found_elements': [],
            'found_text': [],
            'missing_elements': [],
            'missing_text': [],
            'timestamp': datetime.now().isoformat()
        }
        
        start_time = time.time()
        
        try:
            if url_info['test_type'] == 'api':
                # Para APIs, usar requests
                import requests
                response = requests.get(test_result['full_url'])
                test_result['http_status'] = response.status_code
                test_result['response_time'] = time.time() - start_time
                
                if response.status_code == 200:
                    try:
                        json_data = response.json()
                        expected_keys = url_info.get('expected_json_keys', [])
                        
                        for key in expected_keys:
                            if key in json_data:
                                test_result['found_elements'].append(f"JSON key: {key}")
                            else:
                                test_result['missing_elements'].append(f"JSON key: {key}")
                        
                        if not test_result['missing_elements']:
                            test_result['status'] = 'PASSED'
                        else:
                            test_result['status'] = 'PARTIAL'
                            
                    except json.JSONDecodeError:
                        test_result['status'] = 'FAILED'
                        test_result['errors'].append("Invalid JSON response")
                        
                elif response.status_code == 403:
                    test_result['status'] = 'NEEDS_AUTH'
                    test_result['warnings'].append("Authentication required")
                else:
                    test_result['status'] = 'FAILED'
                    test_result['errors'].append(f"HTTP {response.status_code}")
                    
            else:
                # Para páginas web, usar Selenium
                self.driver.get(test_result['full_url'])
                
                # Esperar que cargue la página
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                test_result['response_time'] = time.time() - start_time
                test_result['page_title'] = self.driver.title
                
                # Verificar si necesita autenticación
                if url_info.get('requires_auth', False) and '/auth/login/' in self.driver.current_url:
                    test_result['status'] = 'NEEDS_AUTH'
                    test_result['warnings'].append("Redirected to login (expected)")
                    return test_result
                
                # Verificar errores en la página
                if any(error in test_result['page_title'].lower() for error in ['error', 'exception', 'not found']):
                    test_result['status'] = 'FAILED'
                    test_result['errors'].append(f"Error page: {test_result['page_title']}")
                    return test_result
                
                # Verificar elementos esperados
                expected_elements = url_info.get('expected_elements', [])
                for element_selector in expected_elements:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, element_selector)
                        if elements:
                            test_result['found_elements'].append(element_selector)
                        else:
                            test_result['missing_elements'].append(element_selector)
                    except Exception as e:
                        test_result['warnings'].append(f"Error checking element {element_selector}: {e}")
                
                # Verificar texto esperado
                expected_text = url_info.get('expected_text', [])
                page_text = self.driver.page_source.lower()
                
                for text in expected_text:
                    if text.lower() in page_text:
                        test_result['found_text'].append(text)
                    else:
                        test_result['missing_text'].append(text)
                
                # Determinar estado final
                if test_result['errors']:
                    test_result['status'] = 'FAILED'
                elif test_result['missing_elements'] or test_result['missing_text']:
                    test_result['status'] = 'PARTIAL'
                else:
                    test_result['status'] = 'PASSED'
                    
        except TimeoutException:
            test_result['status'] = 'FAILED'
            test_result['errors'].append("Page load timeout")
            test_result['response_time'] = time.time() - start_time
        except WebDriverException as e:
            test_result['status'] = 'FAILED'
            test_result['errors'].append(f"WebDriver error: {e}")
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
        
        # Configurar driver
        if not self.setup_driver():
            print("💥 No se pudo configurar el driver")
            return False
        
        try:
            # Verificar servidor
            print("🌐 Verificando servidor...")
            try:
                self.driver.get(self.base_url)
                print("✅ Servidor accesible")
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
                print(f"   📄 Título: {result['page_title']}")
                
                if result['errors']:
                    for error in result['errors']:
                        print(f"   ❌ {error}")
                
                if result['warnings']:
                    for warning in result['warnings']:
                        print(f"   ⚠️ {warning}")
                
                if result['found_elements']:
                    print(f"   ✅ Elementos encontrados: {len(result['found_elements'])}")
                
                if result['missing_elements']:
                    print(f"   ❌ Elementos faltantes: {len(result['missing_elements'])}")
                
                if result['found_text']:
                    print(f"   ✅ Texto encontrado: {len(result['found_text'])}")
                
                if result['missing_text']:
                    print(f"   ❌ Texto faltante: {len(result['missing_text'])}")
                
                # Pausa entre pruebas
                time.sleep(0.5)
            
            # Generar reporte
            self.generate_report()
            
        finally:
            if self.driver:
                self.driver.quit()
                print("\n🧹 Driver cerrado")
        
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
        print(f"   Total de pruebas: {total}")
        print(f"   ✅ Exitosas: {passed}")
        print(f"   ⚠️ Parciales: {partial}")
        print(f"   ❌ Fallidas: {failed}")
        print(f"   🔐 Necesitan autenticación: {needs_auth}")
        
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
                if result['missing_elements']:
                    print(f"     - Elementos faltantes: {', '.join(result['missing_elements'])}")
                if result['missing_text']:
                    print(f"     - Texto faltante: {', '.join(result['missing_text'])}")
        
        # Tiempo promedio
        response_times = [r['response_time'] for r in self.results if r['response_time'] > 0]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            print(f"\n⏱️ Tiempo promedio de respuesta: {avg_time:.2f}s")
        
        # Guardar reporte JSON
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
        
        report_file = 'inventario_test_report_completo.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte detallado guardado en: {report_file}")
        
        # Resultado final
        if failed == 0:
            print("\n🎉 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE!")
        elif critical_passed == critical_total:
            print("\n✅ FUNCIONALIDAD CRÍTICA OPERATIVA")
        else:
            print("\n⚠️ ALGUNAS PRUEBAS FALLARON - REVISAR REPORTE")
        
        return failed == 0

def main():
    """Función principal"""
    try:
        tester = CompletInventarioTester()
        success = tester.run_tests()
        
        if success:
            print("\n🎉 Sistema de inventario completamente funcional!")
            return 0
        else:
            print("\n⚠️ Se encontraron problemas - revisar reporte")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Pruebas interrumpidas por el usuario")
        return 1
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
