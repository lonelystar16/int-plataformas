#!/usr/bin/env python
"""
Script automatizado para probar todas las URLs del sistema de inventario
Verifica que las URLs respondan correctamente y no tengan errores.
"""

import os
import sys
import django
import requests
from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from colorama import Fore, Style, init
import time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ferramas.settings')
django.setup()

# Inicializar colorama para colores en terminal
init(autoreset=True)

class URLTester:
    def __init__(self):
        self.client = Client()
        self.base_url = "http://127.0.0.1:8000"
        self.results = []
        self.admin_user = None
        self.regular_user = None
        
    def setup_users(self):
        """Crear usuarios de prueba"""
        print(f"{Fore.BLUE}📋 Configurando usuarios de prueba...{Style.RESET_ALL}")
        
        # Usuario admin
        self.admin_user, created = User.objects.get_or_create(
            username='admin_test',
            defaults={
                'email': 'admin@test.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            self.admin_user.set_password('admin123')
            self.admin_user.save()
            print(f"  ✅ Usuario admin creado: {self.admin_user.username}")
        else:
            print(f"  ℹ️  Usuario admin ya existe: {self.admin_user.username}")
        
        # Usuario regular
        self.regular_user, created = User.objects.get_or_create(
            username='user_test',
            defaults={
                'email': 'user@test.com',
                'is_staff': False,
                'is_superuser': False
            }
        )
        if created:
            self.regular_user.set_password('user123')
            self.regular_user.save()
            print(f"  ✅ Usuario regular creado: {self.regular_user.username}")
        else:
            print(f"  ℹ️  Usuario regular ya existe: {self.regular_user.username}")
    
    def login_as_admin(self):
        """Iniciar sesión como admin"""
        return self.client.login(username='admin_test', password='admin123')
    
    def login_as_user(self):
        """Iniciar sesión como usuario regular"""
        return self.client.login(username='user_test', password='user123')
    
    def logout(self):
        """Cerrar sesión"""
        self.client.logout()
    
    def test_url(self, url_name, url_path, method='GET', login_required=False, admin_required=False, expected_status=200):
        """Probar una URL específica"""
        try:
            # Configurar autenticación
            if admin_required:
                login_success = self.login_as_admin()
                if not login_success:
                    return self.log_result(url_name, url_path, 'FAIL', 'No se pudo autenticar como admin')
            elif login_required:
                login_success = self.login_as_user()
                if not login_success:
                    return self.log_result(url_name, url_path, 'FAIL', 'No se pudo autenticar como usuario')
            
            # Realizar petición
            if method.upper() == 'GET':
                response = self.client.get(url_path)
            elif method.upper() == 'POST':
                response = self.client.post(url_path, {})
            
            # Verificar respuesta
            if response.status_code == expected_status:
                status = 'PASS'
                message = f'Status: {response.status_code}'
            elif response.status_code == 302 and not login_required:
                status = 'REDIRECT'
                message = f'Redirige a login (esperado): {response.status_code}'
            elif response.status_code == 403 and not admin_required:
                status = 'PERMISSION'
                message = f'Acceso denegado (esperado): {response.status_code}'
            else:
                status = 'FAIL'
                message = f'Status inesperado: {response.status_code} (esperado: {expected_status})'
            
            return self.log_result(url_name, url_path, status, message)
            
        except Exception as e:
            return self.log_result(url_name, url_path, 'ERROR', str(e))
        finally:
            self.logout()
    
    def log_result(self, url_name, url_path, status, message):
        """Registrar resultado de prueba"""
        result = {
            'url_name': url_name,
            'url_path': url_path,
            'status': status,
            'message': message,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.results.append(result)
        
        # Colorear salida según resultado
        if status == 'PASS':
            color = Fore.GREEN
            icon = '✅'
        elif status == 'REDIRECT':
            color = Fore.YELLOW
            icon = '🔄'
        elif status == 'PERMISSION':
            color = Fore.CYAN
            icon = '🔒'
        elif status == 'FAIL':
            color = Fore.RED
            icon = '❌'
        else:  # ERROR
            color = Fore.MAGENTA
            icon = '💥'
        
        print(f"  {color}{icon} {url_name:<30} {url_path:<40} {status:<10} {message}{Style.RESET_ALL}")
        return result
    
    def test_server_availability(self):
        """Verificar que el servidor Django esté ejecutándose"""
        print(f"{Fore.BLUE}🔍 Verificando disponibilidad del servidor...{Style.RESET_ALL}")
        try:
            response = requests.get(self.base_url, timeout=5)
            if response.status_code in [200, 302, 404]:
                print(f"  ✅ Servidor Django disponible en {self.base_url}")
                return True
            else:
                print(f"  ❌ Servidor responde con código: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error conectando al servidor: {e}")
            print(f"  💡 Asegúrate de que el servidor Django esté ejecutándose:")
            print(f"     python manage.py runserver")
            return False
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print(f"{Fore.CYAN}🚀 Iniciando pruebas automatizadas de URLs del sistema de inventario{Style.RESET_ALL}")
        print("=" * 80)
        
        # Verificar servidor
        if not self.test_server_availability():
            return
        
        # Configurar usuarios
        self.setup_users()
        
        print(f"\n{Fore.BLUE}🧪 Ejecutando pruebas de URLs...{Style.RESET_ALL}")
        print(f"{'URL Name':<30} {'URL Path':<40} {'Status':<10} {'Message'}")
        print("-" * 100)
        
        # URLs principales (sin autenticación)
        urls_publicas = [
            ('index', '/'),
            ('login', '/auth/login/'),
            ('register', '/auth/register/'),
        ]
        
        for url_name, url_path in urls_publicas:
            self.test_url(url_name, url_path, login_required=False, expected_status=200)
        
        # URLs de inventario (requieren autenticación de admin)
        urls_inventario = [
            ('dashboard_inventario', '/inventario/'),
            ('lista_productos_inventario', '/inventario/productos/'),
            ('entrada_inventario', '/inventario/entrada/'),
            ('salida_inventario', '/inventario/salida/'),
            ('gestionar_alertas', '/inventario/alertas/'),
            ('reporte_inventario', '/inventario/reporte/'),
        ]
        
        for url_name, url_path in urls_inventario:
            self.test_url(url_name, url_path, login_required=True, admin_required=True, expected_status=200)
        
        # URLs de detalle (requieren parámetros)
        from app.domain.models import Producto
        try:
            primer_producto = Producto.objects.first()
            if primer_producto:
                self.test_url(
                    'detalle_producto_inventario',
                    f'/inventario/productos/{primer_producto.id}/',
                    login_required=True,
                    admin_required=True,
                    expected_status=200
                )
                self.test_url(
                    'api_stock_producto',
                    f'/api/inventario/stock/{primer_producto.id}/',
                    login_required=True,
                    admin_required=True,
                    expected_status=200
                )
            else:
                print(f"  ⚠️  No se encontraron productos para probar URLs con parámetros")
        except Exception as e:
            print(f"  ❌ Error al probar URLs con parámetros: {e}")
        
        # URLs que no existen (deben dar 404)
        urls_inexistentes = [
            ('url_inexistente', '/inventario/inexistente/'),
            ('producto_inexistente', '/inventario/productos/99999/'),
        ]
        
        for url_name, url_path in urls_inexistentes:
            self.test_url(url_name, url_path, login_required=True, admin_required=True, expected_status=404)
        
        # Mostrar resumen
        self.show_summary()
    
    def show_summary(self):
        """Mostrar resumen de resultados"""
        print("\n" + "=" * 80)
        print(f"{Fore.CYAN}📊 RESUMEN DE PRUEBAS{Style.RESET_ALL}")
        print("=" * 80)
        
        total = len(self.results)
        passed = len([r for r in self.results if r['status'] == 'PASS'])
        redirects = len([r for r in self.results if r['status'] == 'REDIRECT'])
        permissions = len([r for r in self.results if r['status'] == 'PERMISSION'])
        failed = len([r for r in self.results if r['status'] == 'FAIL'])
        errors = len([r for r in self.results if r['status'] == 'ERROR'])
        
        print(f"📋 Total de pruebas: {total}")
        print(f"✅ Exitosas: {Fore.GREEN}{passed}{Style.RESET_ALL}")
        print(f"🔄 Redirecciones: {Fore.YELLOW}{redirects}{Style.RESET_ALL}")
        print(f"🔒 Permisos: {Fore.CYAN}{permissions}{Style.RESET_ALL}")
        print(f"❌ Fallidas: {Fore.RED}{failed}{Style.RESET_ALL}")
        print(f"💥 Errores: {Fore.MAGENTA}{errors}{Style.RESET_ALL}")
        
        # Porcentaje de éxito
        success_rate = ((passed + redirects + permissions) / total) * 100 if total > 0 else 0
        print(f"\n🎯 Tasa de éxito: {Fore.GREEN}{success_rate:.1f}%{Style.RESET_ALL}")
        
        # Mostrar errores y fallos
        if failed > 0 or errors > 0:
            print(f"\n{Fore.RED}❌ PROBLEMAS ENCONTRADOS:{Style.RESET_ALL}")
            for result in self.results:
                if result['status'] in ['FAIL', 'ERROR']:
                    print(f"  🔴 {result['url_name']}: {result['message']}")
        
        # Recomendaciones
        print(f"\n{Fore.BLUE}💡 RECOMENDACIONES:{Style.RESET_ALL}")
        if failed > 0:
            print("  - Revisa las URLs que fallaron para identificar problemas")
        if errors > 0:
            print("  - Verifica que todas las vistas estén correctamente implementadas")
        if redirects > 0:
            print("  - Las redirecciones son normales para URLs protegidas")
        if permissions > 0:
            print("  - Los errores de permisos son esperados para usuarios no autorizados")
        
        print("  - Asegúrate de que el servidor Django esté ejecutándose")
        print("  - Verifica que las migraciones estén aplicadas")
        print("  - Confirma que existan productos en la base de datos")
    
    def generate_report(self):
        """Generar reporte en archivo"""
        filename = f"url_test_report_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("REPORTE DE PRUEBAS DE URLs - SISTEMA DE INVENTARIO\n")
            f.write("=" * 60 + "\n")
            f.write(f"Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total de pruebas: {len(self.results)}\n\n")
            
            for result in self.results:
                f.write(f"URL: {result['url_name']}\n")
                f.write(f"Path: {result['url_path']}\n")
                f.write(f"Status: {result['status']}\n")
                f.write(f"Message: {result['message']}\n")
                f.write(f"Timestamp: {result['timestamp']}\n")
                f.write("-" * 40 + "\n")
        
        print(f"\n📄 Reporte generado: {filepath}")

def main():
    """Función principal"""
    tester = URLTester()
    tester.run_all_tests()
    tester.generate_report()

if __name__ == "__main__":
    main()
