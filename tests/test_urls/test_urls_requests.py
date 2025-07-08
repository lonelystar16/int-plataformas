#!/usr/bin/env python3
"""
Script de pruebas automatizadas para URLs del sistema de inventario
Usando requests para pruebas HTTP básicas (sin JavaScript)
"""

import os
import sys
import time
import json
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Agregar el directorio del proyecto al PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class InventarioURLTester:
    """Clase para probar todas las URLs del sistema de inventario usando requests"""
    
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
        self.test_user = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        # Configurar retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        
        # URLs a probar
        self.urls_to_test = [
            # URLs públicas
            {
                'name': 'Página Principal',
                'url': '/',
                'requires_auth': False,
                'expected_status': 200,
                'expected_content': ['Ferramas', 'body', 'html']
            },
            
            # URLs de autenticación
            {
                'name': 'Página de Login',
                'url': '/auth/login/',
                'requires_auth': False,
                'expected_status': 200,
                'expected_content': ['login', 'username', 'password']
            },
            
            # URLs de inventario (requieren autenticación)
            {
                'name': 'Dashboard de Inventario',
                'url': '/inventario/',
                'requires_auth': True,
                'expected_status': 200,
                'expected_content': ['Dashboard', 'inventario', 'productos']
            },
            {
                'name': 'Lista de Productos',
                'url': '/inventario/productos/',
                'requires_auth': True,
                'expected_status': 200,
                'expected_content': ['productos', 'tabla', 'stock']
            },
            {
                'name': 'Detalle de Producto',
                'url': '/inventario/productos/1/',
                'requires_auth': True,
                'expected_status': 200,
                'expected_content': ['detalle', 'stock', 'producto']
            },
            {
                'name': 'Entrada de Inventario',
                'url': '/inventario/entrada/',
                'requires_auth': True,
                'expected_status': 200,
                'expected_content': ['entrada', 'form', 'producto']
            },
            {
                'name': 'Salida de Inventario',
                'url': '/inventario/salida/',
                'requires_auth': True,
                'expected_status': 200,
                'expected_content': ['salida', 'form', 'producto']
            },
            {
                'name': 'Gestión de Alertas',
                'url': '/inventario/alertas/',
                'requires_auth': True,
                'expected_status': 200,
                'expected_content': ['alertas', 'gestión', 'inventario']
            },
            {
                'name': 'Reportes de Inventario',
                'url': '/inventario/reporte/',
                'requires_auth': True,
                'expected_status': 200,
                'expected_content': ['reporte', 'inventario', 'fecha']
            },
            
            # API endpoints
            {
                'name': 'API Stock Producto',
                'url': '/api/inventario/stock/1/',
                'requires_auth': True,
                'expected_status': 200,
                'is_api': True,
                'expected_json_keys': ['producto_id', 'stock_disponible']
            },
            
            # URLs adicionales para verificar errores comunes
            {
                'name': 'URL Inexistente (404)',
                'url': '/url-que-no-existe/',
                'requires_auth': False,
                'expected_status': 404,
                'expected_content': ['404', 'not found']
            }
        ]
    
    def login(self):
        """Hacer login para acceder a páginas protegidas"""
        try:
            # Primero obtener la página de login para el CSRF token
            login_url = f"{self.base_url}/auth/login/"
            response = self.session.get(login_url)
            
            if response.status_code != 200:
                print(f"❌ No se pudo acceder a la página de login: {response.status_code}")
                return False
            
            # Buscar el CSRF token
            csrf_token = None
            if 'csrftoken' in self.session.cookies:
                csrf_token = self.session.cookies['csrftoken']
            elif 'csrf_token' in response.text:
                # Buscar en el HTML
                import re
                csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
                if csrf_match:
                    csrf_token = csrf_match.group(1)
            
            if not csrf_token:
                print("⚠️  No se encontró CSRF token, intentando login sin él")
            
            # Datos de login
            login_data = {
                'username': self.test_user['username'],
                'password': self.test_user['password'],
            }
            
            if csrf_token:
                login_data['csrfmiddlewaretoken'] = csrf_token
            
            # Realizar login
            response = self.session.post(login_url, data=login_data)
            
            # Verificar si el login fue exitoso
            if response.status_code == 200 and 'login' not in response.url:
                print("✅ Login exitoso")
                return True
            elif response.status_code == 302:
                print("✅ Login exitoso (redirigido)")
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
            'response_time': 0,
            'status_code': 0,
            'errors': [],
            'warnings': [],
            'found_content': [],
            'timestamp': datetime.now().isoformat()
        }
        
        start_time = time.time()
        
        try:
            # Realizar petición HTTP
            response = self.session.get(test_result['full_url'], timeout=10)
            test_result['response_time'] = time.time() - start_time
            test_result['status_code'] = response.status_code
            
            # Verificar status code esperado
            expected_status = url_info.get('expected_status', 200)
            if response.status_code == expected_status:
                test_result['found_content'].append(f"Status code: {response.status_code}")
            else:
                test_result['errors'].append(f"Expected status {expected_status}, got {response.status_code}")
            
            # Verificar contenido esperado
            if url_info.get('is_api', False):
                # Para APIs, verificar JSON
                try:
                    json_data = response.json()
                    expected_keys = url_info.get('expected_json_keys', [])
                    
                    for key in expected_keys:
                        if key in json_data:
                            test_result['found_content'].append(f"JSON key: {key}")
                        else:
                            test_result['errors'].append(f"Missing JSON key: {key}")
                            
                except json.JSONDecodeError:
                    test_result['errors'].append("Invalid JSON response")
            
            else:
                # Para páginas web, verificar contenido HTML
                content_lower = response.text.lower()
                expected_content = url_info.get('expected_content', [])
                
                for content in expected_content:
                    if content.lower() in content_lower:
                        test_result['found_content'].append(f"Content: {content}")
                    else:
                        test_result['warnings'].append(f"Content not found: {content}")
                
                # Verificar errores comunes de Django
                if 'templatedoesnotexist' in content_lower:
                    test_result['errors'].append("Template error detected")
                
                if 'noreversematch' in content_lower:
                    test_result['errors'].append("URL reverse error detected")
                
                if 'server error' in content_lower:
                    test_result['errors'].append("Server error detected")
                
                if 'traceback' in content_lower and 'django' in content_lower:
                    test_result['errors'].append("Django traceback detected")
            
            # Determinar el estado final
            if test_result['errors']:
                test_result['status'] = 'FAILED'
            elif test_result['warnings']:
                test_result['status'] = 'PASSED_WITH_WARNINGS'
            else:
                test_result['status'] = 'PASSED'
        
        except requests.exceptions.Timeout:
            test_result['errors'].append("Request timeout")
            test_result['status'] = 'FAILED'
            test_result['response_time'] = time.time() - start_time
        
        except requests.exceptions.ConnectionError:
            test_result['errors'].append("Connection error")
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
        
        # Verificar que el servidor esté corriendo
        try:
            response = requests.get(self.base_url, timeout=5)
            print(f"✅ Servidor accesible en {self.base_url}")
        except requests.RequestException as e:
            print(f"❌ No se puede conectar al servidor en {self.base_url}: {e}")
            return False
        
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
            print(f"   🌐 HTTP {result['status_code']}")
            print(f"   🕐 Tiempo: {result['response_time']:.2f}s")
            
            if result['errors']:
                print(f"   ❌ Errores: {', '.join(result['errors'])}")
            
            if result['warnings']:
                print(f"   ⚠️  Advertencias: {', '.join(result['warnings'])}")
            
            if result['found_content']:
                print(f"   ✓ Contenido encontrado: {len(result['found_content'])}")
        
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
        
        # Mostrar estadísticas de tiempo de respuesta
        response_times = [r['response_time'] for r in self.results if r['response_time'] > 0]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            print(f"\n⏱️  Tiempos de respuesta:")
            print(f"   • Promedio: {avg_time:.2f}s")
            print(f"   • Máximo: {max_time:.2f}s")
            print(f"   • Mínimo: {min_time:.2f}s")
        
        # Guardar reporte en archivo JSON
        report_file = 'test_urls_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'base_url': self.base_url,
                'summary': {
                    'total': total_tests,
                    'passed': passed_tests,
                    'warnings': warning_tests,
                    'failed': failed_tests,
                    'success_rate': success_rate,
                    'avg_response_time': sum(response_times) / len(response_times) if response_times else 0
                },
                'results': self.results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte detallado guardado en: {report_file}")
        
        # Generar reporte HTML
        self.generate_html_report()
    
    def generate_html_report(self):
        """Generar reporte HTML"""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r['status'] == 'PASSED'])
        warning_tests = len([r for r in self.results if r['status'] == 'PASSED_WITH_WARNINGS'])
        failed_tests = len([r for r in self.results if r['status'] == 'FAILED'])
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Reporte de Pruebas de URLs - Sistema de Inventario</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f8f9fa; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; text-align: center; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 12px; border-left: 4px solid #007bff; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }}
        .stat-value {{ font-size: 2.5em; font-weight: bold; margin-bottom: 10px; }}
        .stat-label {{ color: #666; font-size: 0.9em; text-transform: uppercase; }}
        .results-table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .results-table th, .results-table td {{ padding: 15px; border-bottom: 1px solid #eee; text-align: left; }}
        .results-table th {{ background: #f8f9fa; font-weight: 600; }}
        .results-table tr:hover {{ background: #f8f9fa; }}
        .status-PASSED {{ color: #28a745; font-weight: bold; }}
        .status-PASSED_WITH_WARNINGS {{ color: #ffc107; font-weight: bold; }}
        .status-FAILED {{ color: #dc3545; font-weight: bold; }}
        .error-list {{ color: #dc3545; font-size: 0.9em; margin-top: 5px; }}
        .warning-list {{ color: #ffc107; font-size: 0.9em; margin-top: 5px; }}
        .success-list {{ color: #28a745; font-size: 0.9em; margin-top: 5px; }}
        .url-code {{ background: #f8f9fa; padding: 4px 8px; border-radius: 4px; font-family: monospace; font-size: 0.9em; }}
        .response-time {{ font-weight: bold; }}
        .fast {{ color: #28a745; }}
        .medium {{ color: #ffc107; }}
        .slow {{ color: #dc3545; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Reporte de Pruebas de URLs</h1>
        <h2>Sistema de Inventario FerramasStore</h2>
        <p>Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        <p>Base URL: {self.base_url}</p>
    </div>
    
    <div class="summary">
        <div class="stat-card">
            <div class="stat-value">{total_tests}</div>
            <div class="stat-label">Total de Pruebas</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: #28a745;">{passed_tests}</div>
            <div class="stat-label">Exitosas</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: #ffc107;">{warning_tests}</div>
            <div class="stat-label">Con Advertencias</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: #dc3545;">{failed_tests}</div>
            <div class="stat-label">Fallidas</div>
        </div>
    </div>
    
    <table class="results-table">
        <thead>
            <tr>
                <th>Nombre de la Prueba</th>
                <th>URL</th>
                <th>Estado</th>
                <th>HTTP Status</th>
                <th>Tiempo de Respuesta</th>
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
            if result['found_content']:
                details.append(f"<div class='success-list'>✓ {len(result['found_content'])} elementos encontrados</div>")
            
            # Clasificar tiempo de respuesta
            time_class = "fast"
            if result['response_time'] > 2:
                time_class = "slow"
            elif result['response_time'] > 1:
                time_class = "medium"
            
            html_content += f"""
            <tr>
                <td><strong>{result['name']}</strong></td>
                <td><code class="url-code">{result['url']}</code></td>
                <td class="status-{result['status']}">{result['status']}</td>
                <td>{result['status_code']}</td>
                <td class="response-time {time_class}">{result['response_time']:.2f}s</td>
                <td>{''.join(details) if details else '<span style="color: #666;">Sin detalles</span>'}</td>
            </tr>
            """
        
        html_content += """
        </tbody>
    </table>
    
    <div style="margin-top: 30px; text-align: center; color: #666;">
        <p>Reporte generado automáticamente por el sistema de pruebas de URLs</p>
    </div>
</body>
</html>
        """
        
        html_file = 'test_urls_report.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📄 Reporte HTML guardado en: {html_file}")

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

if __name__ == "__main__":
    main()
