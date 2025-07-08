#!/usr/bin/env python3
"""
Script de pruebas automatizadas para URLs del sistema de inventario
Usando Selenium WebDriver para verificar funcionalidad completa
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
import requests

# Agregar el directorio del proyecto al PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class InventarioURLTester:
    """Clase para probar todas las URLs del sistema de inventario"""
    
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.driver = None
        self.results = []
        self.test_user = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        # URLs a probar
        self.urls_to_test = [
            # URLs públicas
            {
                'name': 'Página Principal',
                'url': '/',
                'requires_auth': False,
                'expected_elements': ['body', 'nav'],
                'expected_text': 'Ferramas'
            },
            
            # URLs de autenticación
            {
                'name': 'Página de Login',
                'url': '/auth/login/',
                'requires_auth': False,
                'expected_elements': ['form', 'input[name="username"]', 'input[name="password"]'],
                'expected_text': 'Iniciar Sesión'
            },
            
            # URLs de inventario (requieren autenticación)
            {
                'name': 'Dashboard de Inventario',
                'url': '/inventario/',
                'requires_auth': True,
                'expected_elements': ['.container', '.card', '.dashboard'],
                'expected_text': 'Dashboard'
            },
            {
                'name': 'Lista de Productos',
                'url': '/inventario/productos/',
                'requires_auth': True,
                'expected_elements': ['table', '.table-container'],
                'expected_text': 'Productos'
            },
            {
                'name': 'Detalle de Producto',
                'url': '/inventario/productos/1/',
                'requires_auth': True,
                'expected_elements': ['.detail-card', '.info-grid'],
                'expected_text': 'Stock'
            },
            {
                'name': 'Entrada de Inventario',
                'url': '/inventario/entrada/',
                'requires_auth': True,
                'expected_elements': ['form', 'select', 'input'],
                'expected_text': 'Entrada'
            },
            {
                'name': 'Salida de Inventario',
                'url': '/inventario/salida/',
                'requires_auth': True,
                'expected_elements': ['form', 'select', 'input'],
                'expected_text': 'Salida'
            },
            {
                'name': 'Gestión de Alertas',
                'url': '/inventario/alertas/',
                'requires_auth': True,
                'expected_elements': ['.tab-navigation', '.alert-card'],
                'expected_text': 'Alertas'
            },
            {
                'name': 'Reportes de Inventario',
                'url': '/inventario/reporte/',
                'requires_auth': True,
                'expected_elements': ['.report-container', 'form'],
                'expected_text': 'Reporte'
            },
            
            # API endpoints
            {
                'name': 'API Stock Producto',
                'url': '/api/inventario/stock/1/',
                'requires_auth': True,
                'is_api': True,
                'expected_json_keys': ['producto_id', 'stock_disponible']
            }
        ]
    
    def setup_driver(self):
        """Configurar el driver de Selenium"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Ejecutar en segundo plano
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Intentar usar ChromeDriverManager primero
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✅ Driver de Chrome configurado con ChromeDriverManager")
            except Exception as e:
                print(f"⚠️ ChromeDriverManager falló: {e}")
                # Intentar usar el driver del sistema si está disponible
                try:
                    self.driver = webdriver.Chrome(options=chrome_options)
                    print("✅ Driver de Chrome configurado con driver del sistema")
                except Exception as e2:
                    print(f"❌ Error con driver del sistema: {e2}")
                    # Como último recurso, intentar con Firefox
                    try:
                        from selenium.webdriver.firefox.options import Options as FirefoxOptions
                        firefox_options = FirefoxOptions()
                        firefox_options.add_argument('--headless')
                        self.driver = webdriver.Firefox(options=firefox_options)
                        print("✅ Driver de Firefox configurado como alternativa")
                    except:
                        raise e2
            
            if hasattr(self.driver, 'execute_script'):
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.implicitly_wait(10)
            
            print("✅ Driver configurado correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error configurando driver: {e}")
            return False
    
    def login(self):
        """Hacer login para acceder a páginas protegidas"""
        try:
            self.driver.get(f"{self.base_url}/auth/login/")
            
            # Esperar a que aparezca el formulario de login
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            
            # Rellenar formulario
            username_input = self.driver.find_element(By.NAME, "username")
            password_input = self.driver.find_element(By.NAME, "password")
            
            username_input.clear()
            username_input.send_keys(self.test_user['username'])
            
            password_input.clear()
            password_input.send_keys(self.test_user['password'])
            
            # Buscar y hacer clic en el botón de envío
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            submit_button.click()
            
            # Esperar a ser redirigido o ver un mensaje
            time.sleep(3)
            
            # Verificar que el login fue exitoso
            current_url = self.driver.current_url
            if '/auth/login/' not in current_url or 'dashboard' in current_url or 'inventario' in current_url:
                print("✅ Login exitoso")
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
            'status': 'PENDING',
            'response_time': 0,
            'errors': [],
            'warnings': [],
            'found_elements': [],
            'timestamp': datetime.now().isoformat()
        }
        
        start_time = time.time()
        
        try:
            if url_info.get('is_api', False):
                # Para endpoints API, usar requests
                response = requests.get(test_result['full_url'])
                test_result['response_time'] = time.time() - start_time
                
                if response.status_code == 200:
                    try:
                        json_data = response.json()
                        expected_keys = url_info.get('expected_json_keys', [])
                        
                        for key in expected_keys:
                            if key in json_data:
                                test_result['found_elements'].append(f"JSON key: {key}")
                            else:
                                test_result['errors'].append(f"Missing JSON key: {key}")
                        
                        if not test_result['errors']:
                            test_result['status'] = 'PASSED'
                        else:
                            test_result['status'] = 'FAILED'
                            
                    except json.JSONDecodeError:
                        test_result['errors'].append("Invalid JSON response")
                        test_result['status'] = 'FAILED'
                else:
                    test_result['errors'].append(f"HTTP {response.status_code}")
                    test_result['status'] = 'FAILED'
            
            else:
                # Para páginas web, usar Selenium
                self.driver.get(test_result['full_url'])
                test_result['response_time'] = time.time() - start_time
                
                # Esperar a que la página cargue
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
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
                expected_text = url_info.get('expected_text')
                if expected_text:
                    page_source = self.driver.page_source.lower()
                    if expected_text.lower() in page_source:
                        test_result['found_elements'].append(f"Text: {expected_text}")
                    else:
                        test_result['warnings'].append(f"Text not found: {expected_text}")
                
                # Verificar que no hay errores 500/404
                if "500" in self.driver.page_source or "404" in self.driver.page_source:
                    test_result['errors'].append("Server error detected")
                
                # Verificar que no hay errores de Django
                if "TemplateDoesNotExist" in self.driver.page_source:
                    test_result['errors'].append("Template error detected")
                
                if "NoReverseMatch" in self.driver.page_source:
                    test_result['errors'].append("URL error detected")
                
                # Determinar el estado final
                if test_result['errors']:
                    test_result['status'] = 'FAILED'
                elif test_result['warnings']:
                    test_result['status'] = 'PASSED_WITH_WARNINGS'
                else:
                    test_result['status'] = 'PASSED'
        
        except TimeoutException:
            test_result['errors'].append("Page load timeout")
            test_result['status'] = 'FAILED'
            test_result['response_time'] = time.time() - start_time
        
        except Exception as e:
            test_result['errors'].append(f"Unexpected error: {str(e)}")
            test_result['status'] = 'FAILED'
            test_result['response_time'] = time.time() - start_time
        
        return test_result
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🚀 Iniciando pruebas de URLs del sistema de inventario...")
        print("=" * 60)
        
        # Configurar driver
        if not self.setup_driver():
            return False
        
        # Verificar que el servidor esté corriendo
        try:
            response = requests.get(self.base_url, timeout=5)
            if response.status_code != 200:
                print(f"❌ El servidor no está respondiendo en {self.base_url}")
                return False
        except requests.RequestException:
            print(f"❌ No se puede conectar al servidor en {self.base_url}")
            return False
        
        print(f"✅ Servidor accesible en {self.base_url}")
        
        # Hacer login una vez
        login_success = self.login()
        if not login_success:
            print("⚠️  Login falló, solo se probarán URLs públicas")
        
        # Probar cada URL
        for url_info in self.urls_to_test:
            print(f"\n🔍 Probando: {url_info['name']}")
            
            # Saltar URLs que requieren autenticación si el login falló
            if url_info.get('requires_auth', False) and not login_success:
                print("⏭️  Saltando (requiere autenticación)")
                continue
            
            result = self.test_url(url_info)
            self.results.append(result)
            
            # Mostrar resultado
            status_emoji = {
                'PASSED': '✅',
                'PASSED_WITH_WARNINGS': '⚠️',
                'FAILED': '❌',
                'PENDING': '⏳'
            }
            
            print(f"   {status_emoji.get(result['status'], '❓')} {result['status']}")
            print(f"   🕐 Tiempo: {result['response_time']:.2f}s")
            
            if result['errors']:
                print(f"   ❌ Errores: {', '.join(result['errors'])}")
            
            if result['warnings']:
                print(f"   ⚠️  Advertencias: {', '.join(result['warnings'])}")
            
            if result['found_elements']:
                print(f"   ✓ Elementos encontrados: {len(result['found_elements'])}")
        
        # Generar reporte final
        self.generate_report()
        
        return True
    
    def generate_report(self):
        """Generar reporte final de pruebas"""
        print("\n" + "=" * 60)
        print("📊 REPORTE FINAL DE PRUEBAS")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r['status'] == 'PASSED'])
        warning_tests = len([r for r in self.results if r['status'] == 'PASSED_WITH_WARNINGS'])
        failed_tests = len([r for r in self.results if r['status'] == 'FAILED'])
        
        print(f"Total de pruebas: {total_tests}")
        print(f"✅ Exitosas: {passed_tests}")
        print(f"⚠️  Con advertencias: {warning_tests}")
        print(f"❌ Fallidas: {failed_tests}")
        
        success_rate = ((passed_tests + warning_tests) / total_tests * 100) if total_tests > 0 else 0
        print(f"📈 Tasa de éxito: {success_rate:.1f}%")
        
        # Mostrar URLs fallidas
        if failed_tests > 0:
            print("\n❌ URLs que fallaron:")
            for result in self.results:
                if result['status'] == 'FAILED':
                    print(f"   • {result['name']}: {', '.join(result['errors'])}")
        
        # Mostrar URLs con advertencias
        if warning_tests > 0:
            print("\n⚠️  URLs con advertencias:")
            for result in self.results:
                if result['status'] == 'PASSED_WITH_WARNINGS':
                    print(f"   • {result['name']}: {', '.join(result['warnings'])}")
        
        # Guardar reporte en archivo JSON
        report_file = 'test_urls_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total': total_tests,
                    'passed': passed_tests,
                    'warnings': warning_tests,
                    'failed': failed_tests,
                    'success_rate': success_rate
                },
                'results': self.results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte detallado guardado en: {report_file}")
        
        # Generar reporte HTML
        self.generate_html_report()
    
    def generate_html_report(self):
        """Generar reporte HTML"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Reporte de Pruebas de URLs - Sistema de Inventario</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }}
        .stat-card {{ background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stat-value {{ font-size: 2em; font-weight: bold; }}
        .stat-label {{ color: #666; }}
        .results-table {{ width: 100%; border-collapse: collapse; }}
        .results-table th, .results-table td {{ padding: 12px; border: 1px solid #ddd; text-align: left; }}
        .results-table th {{ background: #f8f9fa; }}
        .status-PASSED {{ color: #28a745; }}
        .status-PASSED_WITH_WARNINGS {{ color: #ffc107; }}
        .status-FAILED {{ color: #dc3545; }}
        .error-list {{ color: #dc3545; font-size: 0.9em; }}
        .warning-list {{ color: #ffc107; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Reporte de Pruebas de URLs - Sistema de Inventario</h1>
        <p>Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <div class="stat-card">
            <div class="stat-value">{len(self.results)}</div>
            <div class="stat-label">Total de Pruebas</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: #28a745;">{len([r for r in self.results if r['status'] == 'PASSED'])}</div>
            <div class="stat-label">Exitosas</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: #ffc107;">{len([r for r in self.results if r['status'] == 'PASSED_WITH_WARNINGS'])}</div>
            <div class="stat-label">Con Advertencias</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: #dc3545;">{len([r for r in self.results if r['status'] == 'FAILED'])}</div>
            <div class="stat-label">Fallidas</div>
        </div>
    </div>
    
    <table class="results-table">
        <thead>
            <tr>
                <th>Nombre</th>
                <th>URL</th>
                <th>Estado</th>
                <th>Tiempo (s)</th>
                <th>Detalles</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for result in self.results:
            details = []
            if result['errors']:
                details.append(f"<div class='error-list'>❌ {', '.join(result['errors'])}</div>")
            if result['warnings']:
                details.append(f"<div class='warning-list'>⚠️ {', '.join(result['warnings'])}</div>")
            if result['found_elements']:
                details.append(f"<div>✓ {len(result['found_elements'])} elementos encontrados</div>")
            
            html_content += f"""
            <tr>
                <td>{result['name']}</td>
                <td><code>{result['url']}</code></td>
                <td class="status-{result['status']}">{result['status']}</td>
                <td>{result['response_time']:.2f}</td>
                <td>{''.join(details) if details else 'Sin detalles'}</td>
            </tr>
            """
        
        html_content += """
        </tbody>
    </table>
</body>
</html>
        """
        
        html_file = 'test_urls_report.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📄 Reporte HTML guardado en: {html_file}")
    
    def cleanup(self):
        """Limpiar recursos"""
        if self.driver:
            self.driver.quit()
            print("🧹 Driver cerrado correctamente")

def main():
    """Función principal"""
    tester = InventarioURLTester()
    
    try:
        success = tester.run_all_tests()
        if success:
            print("\n🎉 Pruebas completadas exitosamente!")
        else:
            print("\n💥 Pruebas fallaron durante la configuración")
    
    except KeyboardInterrupt:
        print("\n⏹️  Pruebas interrumpidas por el usuario")
    
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
    
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()
