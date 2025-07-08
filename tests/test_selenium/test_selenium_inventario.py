#!/usr/bin/env python3
"""
Script de pruebas automatizadas para URLs del sistema de inventario
Usando Selenium WebDriver - Versión mejorada
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

class InventarioSeleniumTester:
    """Clase para probar todas las URLs del sistema de inventario con Selenium"""
    
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.driver = None
        self.results = []
        self.test_user = {
            'username': 'admin',
            'password': 'admin123'
        }
        self.logged_in = False
        
        # URLs a probar
        self.urls_to_test = [
            # URLs públicas
            {
                'name': 'Página Principal',
                'url': '/',
                'requires_auth': False,
                'expected_elements': ['body', 'main'],
                'expected_text': 'Ferramas'
            },
            {
                'name': 'Página de Login',
                'url': '/auth/login/',
                'requires_auth': False,
                'expected_elements': ['form', 'input[name="usuario"]', 'input[name="password"]'],
                'expected_text': 'Iniciar Sesión'
            },
            {
                'name': 'Página de Registro',
                'url': '/auth/register/',
                'requires_auth': False,
                'expected_elements': ['form', 'input[name="nombre"]'],
                'expected_text': 'Registro'
            },
            
            # URLs de inventario (requieren autenticación)
            {
                'name': 'Dashboard de Inventario',
                'url': '/inventario/',
                'requires_auth': True,
                'expected_elements': ['.container', '.card-container'],
                'expected_text': 'Dashboard'
            },
            {
                'name': 'Lista de Productos',
                'url': '/inventario/productos/',
                'requires_auth': True,
                'expected_elements': ['table', '.product-table'],
                'expected_text': 'Lista de Productos'
            },
            {
                'name': 'Entrada de Inventario',
                'url': '/inventario/entrada/',
                'requires_auth': True,
                'expected_elements': ['form', 'select[name="producto"]'],
                'expected_text': 'Entrada de Inventario'
            },
            {
                'name': 'Salida de Inventario',
                'url': '/inventario/salida/',
                'requires_auth': True,
                'expected_elements': ['form', 'select[name="producto"]'],
                'expected_text': 'Salida de Inventario'
            },
            {
                'name': 'Gestión de Alertas',
                'url': '/inventario/alertas/',
                'requires_auth': True,
                'expected_elements': ['.tab-navigation', '.alerts-container'],
                'expected_text': 'Gestión de Alertas'
            },
            {
                'name': 'Reportes de Inventario',
                'url': '/inventario/reporte/',
                'requires_auth': True,
                'expected_elements': ['.report-container', 'form'],
                'expected_text': 'Reporte de Inventario'
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
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Intentar usar ChromeDriverManager primero
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✅ Driver configurado con ChromeDriverManager")
            except:
                # Como alternativa, usar el driver del sistema
                self.driver = webdriver.Chrome(options=chrome_options)
                print("✅ Driver configurado con driver del sistema")
            
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
        """Hacer login para acceder a páginas protegidas"""
        try:
            print("🔐 Iniciando proceso de login...")
            
            # Navegar a la página de login
            self.driver.get(f"{self.base_url}/auth/login/")
            
            # Esperar a que aparezca el formulario de login
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "usuario"))
            )
            
            # Rellenar formulario
            username_input = self.driver.find_element(By.NAME, "usuario")
            password_input = self.driver.find_element(By.NAME, "password")
            
            username_input.clear()
            username_input.send_keys(self.test_user['username'])
            
            password_input.clear()
            password_input.send_keys(self.test_user['password'])
            
            # Buscar y hacer clic en el botón de envío
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            submit_button.click()
            
            # Esperar a que se complete el login
            time.sleep(3)
            
            # Verificar que el login fue exitoso
            current_url = self.driver.current_url
            if '/auth/login/' not in current_url:
                print("✅ Login exitoso")
                self.logged_in = True
                return True
            else:
                # Verificar si hay mensajes de error
                try:
                    error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".alert-danger, .error-message, .alert-error")
                    if error_elements:
                        error_text = error_elements[0].text
                        print(f"❌ Login falló: {error_text}")
                    else:
                        print("❌ Login falló: razón desconocida")
                except:
                    print("❌ Login falló: sin redireccionamiento")
                
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
            'response_time': 0,
            'errors': [],
            'warnings': [],
            'found_elements': [],
            'page_title': '',
            'timestamp': datetime.now().isoformat()
        }
        
        start_time = time.time()
        
        try:
            # Navegar a la URL
            self.driver.get(test_result['full_url'])
            
            # Esperar a que la página cargue
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            test_result['response_time'] = time.time() - start_time
            
            # Obtener título de la página
            try:
                test_result['page_title'] = self.driver.title
            except:
                test_result['page_title'] = "No title"
            
            # Verificar si necesita autenticación y estamos en login
            if url_info.get('requires_auth', False) and '/auth/login/' in self.driver.current_url:
                test_result['status'] = 'NEEDS_AUTH'
                test_result['warnings'].append("Redirigido a login (esperado)")
                return test_result
            
            # Verificar elementos esperados
            expected_elements = url_info.get('expected_elements', [])
            for element_selector in expected_elements:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, element_selector)
                    if elements:
                        test_result['found_elements'].append(element_selector)
                    else:
                        test_result['warnings'].append(f"Element not found: {element_selector}")
                except Exception as e:
                    test_result['warnings'].append(f"Error checking element {element_selector}: {e}")
            
            # Verificar texto esperado
            expected_text = url_info.get('expected_text', '')
            if expected_text:
                try:
                    page_text = self.driver.page_source.lower()
                    if expected_text.lower() in page_text:
                        test_result['found_elements'].append(f"Text: {expected_text}")
                    else:
                        test_result['warnings'].append(f"Text not found: {expected_text}")
                except Exception as e:
                    test_result['warnings'].append(f"Error checking text: {e}")
            
            # Verificar errores en la página
            try:
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".alert-danger, .error-message, .alert-error")
                if error_elements:
                    for error_elem in error_elements:
                        if error_elem.text.strip():
                            test_result['errors'].append(f"Page error: {error_elem.text.strip()}")
            except:
                pass
            
            # Verificar si es una página de error 404/500
            if "404" in test_result['page_title'] or "500" in test_result['page_title']:
                test_result['errors'].append("Error page detected")
            
            # Determinar estado final
            if test_result['errors']:
                test_result['status'] = 'FAILED'
            elif test_result['warnings'] and not test_result['found_elements']:
                test_result['status'] = 'WARNING'
            else:
                test_result['status'] = 'PASSED'
            
        except TimeoutException:
            test_result['status'] = 'FAILED'
            test_result['errors'].append("Page load timeout")
            test_result['response_time'] = time.time() - start_time
        except Exception as e:
            test_result['status'] = 'FAILED'
            test_result['errors'].append(f"Unexpected error: {e}")
            test_result['response_time'] = time.time() - start_time
        
        return test_result
    
    def run_tests(self):
        """Ejecutar todas las pruebas"""
        print("🚀 Iniciando pruebas de Selenium para el sistema de inventario...")
        print("=" * 70)
        
        # Configurar driver
        if not self.setup_driver():
            print("💥 No se pudo configurar el driver. Terminando.")
            return False
        
        try:
            # Verificar que el servidor esté accesible
            print("🌐 Verificando accesibilidad del servidor...")
            try:
                self.driver.get(self.base_url)
                print("✅ Servidor accesible")
            except Exception as e:
                print(f"❌ Servidor no accesible: {e}")
                return False
            
            # Intentar login
            if not self.login():
                print("⚠️ Login falló, solo se probarán URLs públicas")
            
            # Ejecutar pruebas
            for url_info in self.urls_to_test:
                print(f"\n🔍 Probando: {url_info['name']}")
                
                # Saltar URLs que requieren autenticación si no estamos logueados
                if url_info.get('requires_auth', False) and not self.logged_in:
                    print("⏭️ Saltando (requiere autenticación)")
                    continue
                
                result = self.test_url(url_info)
                self.results.append(result)
                
                # Mostrar resultado
                status_icons = {
                    'PASSED': '✅',
                    'WARNING': '⚠️',
                    'FAILED': '❌',
                    'NEEDS_AUTH': '🔐'
                }
                
                icon = status_icons.get(result['status'], '❓')
                print(f"   {icon} {result['status']}")
                print(f"   🕐 Tiempo: {result['response_time']:.2f}s")
                print(f"   📄 Título: {result['page_title']}")
                
                if result['errors']:
                    for error in result['errors']:
                        print(f"   ❌ {error}")
                
                if result['warnings']:
                    for warning in result['warnings']:
                        print(f"   ⚠️ {warning}")
                
                if result['found_elements']:
                    print(f"   ✓ Elementos encontrados: {len(result['found_elements'])}")
                
                # Pequeña pausa entre pruebas
                time.sleep(1)
            
            # Generar reporte
            self.generate_report()
            
        finally:
            # Cerrar el driver
            if self.driver:
                self.driver.quit()
                print("\n🧹 Driver cerrado correctamente")
        
        return True
    
    def generate_report(self):
        """Generar reporte de resultados"""
        print("\n" + "=" * 70)
        print("📊 REPORTE FINAL DE PRUEBAS")
        print("=" * 70)
        
        passed = len([r for r in self.results if r['status'] == 'PASSED'])
        failed = len([r for r in self.results if r['status'] == 'FAILED'])
        warnings = len([r for r in self.results if r['status'] == 'WARNING'])
        needs_auth = len([r for r in self.results if r['status'] == 'NEEDS_AUTH'])
        
        print(f"Total de pruebas: {len(self.results)}")
        print(f"✅ Exitosas: {passed}")
        print(f"⚠️ Con advertencias: {warnings}")
        print(f"❌ Fallidas: {failed}")
        print(f"🔐 Necesitan autenticación: {needs_auth}")
        
        if len(self.results) > 0:
            success_rate = (passed / len(self.results)) * 100
            print(f"📈 Tasa de éxito: {success_rate:.1f}%")
        
        # Mostrar URLs que fallaron
        failed_urls = [r for r in self.results if r['status'] == 'FAILED']
        if failed_urls:
            print("\n❌ URLs que fallaron:")
            for result in failed_urls:
                print(f"   • {result['name']}: {', '.join(result['errors'])}")
        
        # Guardar reporte JSON
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'base_url': self.base_url,
            'logged_in': self.logged_in,
            'summary': {
                'total': len(self.results),
                'passed': passed,
                'failed': failed,
                'warnings': warnings,
                'needs_auth': needs_auth,
                'success_rate': (passed / len(self.results) * 100) if self.results else 0
            },
            'results': self.results
        }
        
        with open('selenium_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte detallado guardado en: selenium_test_report.json")
        
        return len(self.results) > 0 and failed == 0

def main():
    """Función principal"""
    try:
        tester = InventarioSeleniumTester()
        success = tester.run_tests()
        
        if success:
            print("\n🎉 Pruebas completadas exitosamente!")
        else:
            print("\n💥 Algunas pruebas fallaron o no se pudieron ejecutar.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")

if __name__ == "__main__":
    main()
