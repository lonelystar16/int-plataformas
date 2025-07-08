#!/usr/bin/env python3
"""
Script de pruebas automatizadas para URLs del sistema de inventario
Usando Django Test Client para pruebas más precisas
"""

import os
import sys
import django
import json
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ferramas.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse, NoReverseMatch

class InventarioURLTester:
    """Clase para probar todas las URLs del sistema de inventario usando Django Test Client"""
    
    def __init__(self):
        self.client = Client()
        self.results = []
        self.test_user = None
        
        # URLs a probar
        self.urls_to_test = [
            # URLs públicas
            {
                'name': 'Página Principal',
                'url': '/',
                'url_name': 'app:index',
                'requires_auth': False,
                'expected_status': 200,
                'expected_content': ['Ferramas', 'navbar']
            },
            
            # URLs de autenticación
            {
                'name': 'Página de Login',
                'url': '/auth/login/',
                'url_name': 'app:login',
                'requires_auth': False,
                'expected_status': 200,
                'expected_content': ['login', 'username', 'password']
            },
            
            # URLs de inventario (requieren autenticación)
            {
                'name': 'Dashboard de Inventario',
                'url': '/inventario/',
                'url_name': 'app:dashboard_inventario',
                'requires_auth': True,
                'expected_status': 200,
                'expected_content': ['Dashboard', 'inventario']
            },
            {
                'name': 'Lista de Productos',
                'url': '/inventario/productos/',
                'url_name': 'app:lista_productos_inventario',
                'requires_auth': True,
                'expected_status': 200,
                'expected_content': ['productos', 'tabla']
            },
            {
                'name': 'Detalle de Producto',
                'url': '/inventario/productos/1/',
                'url_name': 'app:detalle_producto_inventario',
                'url_kwargs': {'producto_id': 1},
                'requires_auth': True,
                'expected_status': 200,
                'expected_content': ['detalle', 'stock']
            },
            {
                'name': 'Entrada de Inventario',
                'url': '/inventario/entrada/',
                'url_name': 'app:entrada_inventario',
                'requires_auth': True,
                'expected_status': 200,
                'expected_content': ['entrada', 'form']
            },
            {
                'name': 'Salida de Inventario',
                'url': '/inventario/salida/',
                'url_name': 'app:salida_inventario',
                'requires_auth': True,
                'expected_status': 200,
                'expected_content': ['salida', 'form']
            },
            {
                'name': 'Gestión de Alertas',
                'url': '/inventario/alertas/',
                'url_name': 'app:gestionar_alertas',
                'requires_auth': True,
                'expected_status': 200,
                'expected_content': ['alertas', 'gestión']
            },
            {
                'name': 'Reportes de Inventario',
                'url': '/inventario/reporte/',
                'url_name': 'app:reporte_inventario',
                'requires_auth': True,
                'expected_status': 200,
                'expected_content': ['reporte', 'inventario']
            },
            
            # API endpoints
            {
                'name': 'API Stock Producto',
                'url': '/api/inventario/stock/1/',
                'url_name': 'app:api_stock_producto',
                'url_kwargs': {'producto_id': 1},
                'requires_auth': True,
                'expected_status': 200,
                'is_api': True,
                'expected_json_keys': ['producto_id', 'stock_disponible']
            }
        ]
    
    def setup_test_user(self):
        """Crear o obtener usuario de prueba"""
        try:
            self.test_user = User.objects.get(username='admin')
            print("✅ Usuario admin encontrado")
            return True
        except User.DoesNotExist:
            print("❌ Usuario admin no encontrado")
            return False
    
    def login(self):
        """Hacer login para acceder a páginas protegidas"""
        if not self.test_user:
            return False
            
        try:
            # Usar force_login para evitar problemas con formularios
            self.client.force_login(self.test_user)
            print("✅ Login exitoso usando force_login")
            return True
        except Exception as e:
            print(f"❌ Error durante login: {e}")
            return False
    
    def test_url_reverse(self, url_info):
        """Probar si la URL se puede resolver por nombre"""
        try:
            if 'url_name' in url_info:
                kwargs = url_info.get('url_kwargs', {})
                reversed_url = reverse(url_info['url_name'], kwargs=kwargs)
                return True, reversed_url
            return True, url_info['url']
        except NoReverseMatch as e:
            return False, str(e)
    
    def test_url(self, url_info):
        """Probar una URL específica"""
        test_result = {
            'name': url_info['name'],
            'url': url_info['url'],
            'url_name': url_info.get('url_name', 'N/A'),
            'status': 'PENDING',
            'status_code': 0,
            'errors': [],
            'warnings': [],
            'found_content': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Primero verificar si la URL se puede resolver
        can_reverse, reversed_url = self.test_url_reverse(url_info)
        if not can_reverse:
            test_result['errors'].append(f"URL reverse failed: {reversed_url}")
            test_result['status'] = 'FAILED'
            return test_result
        
        test_result['resolved_url'] = reversed_url
        
        try:
            # Realizar petición HTTP usando Django Test Client
            response = self.client.get(reversed_url)
            test_result['status_code'] = response.status_code
            
            # Verificar status code esperado
            expected_status = url_info.get('expected_status', 200)
            
            # Si requiere autenticación y obtenemos 302, es redirección al login
            if url_info.get('requires_auth', False) and response.status_code == 302:
                if '/auth/login/' in response.url:
                    test_result['errors'].append("Redirected to login (authentication required)")
                else:
                    test_result['found_content'].append(f"Redirected to: {response.url}")
            elif response.status_code == expected_status:
                test_result['found_content'].append(f"Status code: {response.status_code}")
            else:
                test_result['errors'].append(f"Expected status {expected_status}, got {response.status_code}")
            
            # Verificar contenido esperado
            if url_info.get('is_api', False):
                # Para APIs, verificar JSON
                try:
                    if hasattr(response, 'json'):
                        json_data = response.json()
                    else:
                        json_data = json.loads(response.content.decode())
                    
                    expected_keys = url_info.get('expected_json_keys', [])
                    
                    for key in expected_keys:
                        if key in json_data:
                            test_result['found_content'].append(f"JSON key: {key}")
                        else:
                            test_result['errors'].append(f"Missing JSON key: {key}")
                            
                except (json.JSONDecodeError, ValueError):
                    test_result['errors'].append("Invalid JSON response")
            
            else:
                # Para páginas web, verificar contenido HTML
                content_str = response.content.decode('utf-8', errors='ignore').lower()
                expected_content = url_info.get('expected_content', [])
                
                for content in expected_content:
                    if content.lower() in content_str:
                        test_result['found_content'].append(f"Content: {content}")
                    else:
                        test_result['warnings'].append(f"Content not found: {content}")
                
                # Verificar errores comunes de Django
                if 'templatedoesnotexist' in content_str:
                    test_result['errors'].append("Template error detected")
                
                if 'noreversematch' in content_str:
                    test_result['errors'].append("URL reverse error detected")
                
                if 'server error' in content_str or response.status_code == 500:
                    test_result['errors'].append("Server error detected")
                
                if 'traceback' in content_str and 'django' in content_str:
                    test_result['errors'].append("Django traceback detected")
            
            # Determinar el estado final
            if test_result['errors']:
                test_result['status'] = 'FAILED'
            elif test_result['warnings']:
                test_result['status'] = 'PASSED_WITH_WARNINGS'
            else:
                test_result['status'] = 'PASSED'
        
        except Exception as e:
            test_result['errors'].append(f"Unexpected error: {str(e)}")
            test_result['status'] = 'FAILED'
        
        return test_result
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🚀 Iniciando pruebas de URLs del sistema de inventario...")
        print("=" * 60)
        
        # Configurar usuario de prueba
        if not self.setup_test_user():
            print("⚠️  Usuario de prueba no disponible, solo se probarán URLs públicas")
            login_success = False
        else:
            login_success = self.login()
        
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
            print(f"   🔗 URL: {result.get('resolved_url', result['url'])}")
            
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
        
        print(f"Total de pruebas ejecutadas: {total_tests}")
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
        report_file = 'test_urls_django_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'framework': 'Django Test Client',
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
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r['status'] == 'PASSED'])
        warning_tests = len([r for r in self.results if r['status'] == 'PASSED_WITH_WARNINGS'])
        failed_tests = len([r for r in self.results if r['status'] == 'FAILED'])
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Reporte de Pruebas de URLs - Django Test Client</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: #f8f9fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 15px; margin-bottom: 30px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
        .header h1 {{ margin: 0; font-size: 2.5em; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 25px; margin-bottom: 40px; }}
        .stat-card {{ background: white; padding: 30px; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); text-align: center; transition: transform 0.3s ease; }}
        .stat-card:hover {{ transform: translateY(-5px); }}
        .stat-value {{ font-size: 3em; font-weight: bold; margin-bottom: 10px; }}
        .stat-label {{ color: #666; font-size: 1em; text-transform: uppercase; letter-spacing: 1px; }}
        .results-container {{ background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 8px 25px rgba(0,0,0,0.1); }}
        .results-table {{ width: 100%; border-collapse: collapse; }}
        .results-table th {{ background: #f8f9fa; padding: 20px; text-align: left; font-weight: 600; border-bottom: 2px solid #dee2e6; }}
        .results-table td {{ padding: 15px 20px; border-bottom: 1px solid #dee2e6; vertical-align: top; }}
        .results-table tr:hover {{ background: #f8f9fa; }}
        .status-PASSED {{ color: #28a745; font-weight: bold; }}
        .status-PASSED_WITH_WARNINGS {{ color: #ffc107; font-weight: bold; }}
        .status-FAILED {{ color: #dc3545; font-weight: bold; }}
        .url-info {{ font-family: 'Courier New', monospace; background: #f8f9fa; padding: 8px 12px; border-radius: 6px; font-size: 0.9em; }}
        .detail-list {{ font-size: 0.9em; margin-top: 8px; }}
        .error-item {{ color: #dc3545; margin: 2px 0; }}
        .warning-item {{ color: #ffc107; margin: 2px 0; }}
        .success-item {{ color: #28a745; margin: 2px 0; }}
        .footer {{ text-align: center; margin-top: 40px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Reporte de Pruebas de URLs</h1>
            <p>Sistema de Inventario FerramasStore - Django Test Client</p>
            <p>Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
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
        
        <div class="results-container">
            <table class="results-table">
                <thead>
                    <tr>
                        <th>Nombre de la Prueba</th>
                        <th>URL / Nombre</th>
                        <th>Estado</th>
                        <th>HTTP Status</th>
                        <th>Detalles</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for result in self.results:
            details = []
            if result['errors']:
                for error in result['errors']:
                    details.append(f"<div class='error-item'>❌ {error}</div>")
            if result['warnings']:
                for warning in result['warnings']:
                    details.append(f"<div class='warning-item'>⚠️ {warning}</div>")
            if result['found_content']:
                for content in result['found_content']:
                    details.append(f"<div class='success-item'>✓ {content}</div>")
            
            html_content += f"""
            <tr>
                <td><strong>{result['name']}</strong></td>
                <td>
                    <div class="url-info">{result['url']}</div>
                    <small>URL Name: {result['url_name']}</small>
                </td>
                <td class="status-{result['status']}">{result['status']}</td>
                <td><strong>{result['status_code']}</strong></td>
                <td>
                    <div class="detail-list">
                        {''.join(details) if details else '<span style="color: #666;">Sin detalles</span>'}
                    </div>
                </td>
            </tr>
            """
        
        html_content += """
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Reporte generado automáticamente por el sistema de pruebas de URLs - Django Test Client</p>
        </div>
    </div>
</body>
</html>
        """
        
        html_file = 'test_urls_django_report.html'
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
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
