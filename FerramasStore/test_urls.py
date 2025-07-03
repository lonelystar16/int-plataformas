#!/usr/bin/env python
"""
Script para verificar que todas las URLs del proyecto funcionen correctamente
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
from django.urls import reverse
from django.core.management import execute_from_command_line

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ferramas.settings')
django.setup()

def test_url_patterns():
    """Verifica que todas las URLs se puedan resolver correctamente"""
    
    # URLs que deberían funcionar
    url_tests = [
        ('app:index', 'Página principal'),
        ('app:herra_manuales', 'Herramientas manuales'),
        ('app:materiales_basicos', 'Materiales básicos'),
        ('app:equipos_seguridad', 'Equipos de seguridad'),
        ('app:tornillos_anclaje', 'Tornillos y anclajes'),
        ('app:fijaciones', 'Fijaciones'),
        ('app:equipos_medicion', 'Equipos de medición'),
        ('app:login', 'Login'),
        ('app:register', 'Registro'),
        ('app:logout', 'Logout'),
        ('app:checkout', 'Checkout'),
        ('app:productos_externos_page', 'Productos externos'),
        ('app:valor_dolar_page', 'Valor del dólar'),
        ('app:crear_pago_page', 'Crear pago'),
        ('app:procesar_pago', 'Procesar pago'),
        ('app:voucher', 'Voucher'),
    ]
    
    print("🔍 Verificando URLs...")
    print("=" * 50)
    
    success_count = 0
    error_count = 0
    
    for url_name, description in url_tests:
        try:
            url = reverse(url_name)
            print(f"✅ {description:25} -> {url}")
            success_count += 1
        except Exception as e:
            print(f"❌ {description:25} -> ERROR: {e}")
            error_count += 1
    
    print("=" * 50)
    print(f"📊 Resultados: {success_count} éxitos, {error_count} errores")
    
    if error_count == 0:
        print("🎉 ¡Todas las URLs funcionan correctamente!")
        return True
    else:
        print("⚠️  Hay URLs que necesitan atención")
        return False

if __name__ == "__main__":
    success = test_url_patterns()
    sys.exit(0 if success else 1)
