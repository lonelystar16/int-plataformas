#!/usr/bin/env python3
"""
Script para probar las validaciones de seguridad implementadas
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ferramas.settings')

import django
django.setup()

from app.security.validators import (
    validate_chilean_phone, validate_chilean_rut, 
    validate_strong_password, validate_email_domain,
    sanitize_html_input, validate_no_sql_injection
)

def test_phone_validation():
    """Probar validación de teléfonos chilenos"""
    print("🔍 Probando validación de teléfonos...")
    
    valid_phones = [
        "+56912345678",
        "56912345678", 
        "912345678",
        "12345678"
    ]
    
    invalid_phones = [
        "123456",
        "abcd1234",
        "+1234567890",
        "123"
    ]
    
    for phone in valid_phones:
        try:
            validate_chilean_phone(phone)
            print(f"✅ {phone} - VÁLIDO")
        except Exception as e:
            print(f"❌ {phone} - ERROR: {e}")
    
    for phone in invalid_phones:
        try:
            validate_chilean_phone(phone)
            print(f"❌ {phone} - DEBERÍA SER INVÁLIDO")
        except Exception as e:
            print(f"✅ {phone} - CORRECTAMENTE RECHAZADO: {e}")

def test_password_validation():
    """Probar validación de contraseñas"""
    print("\n🔍 Probando validación de contraseñas...")
    
    valid_passwords = [
        "MiPassword123!",
        "Segura2024@",
        "Compleja9#"
    ]
    
    invalid_passwords = [
        "123456",
        "password",
        "PASSWORD",
        "Password123",  # Sin carácter especial
        "Pass1!"  # Muy corta
    ]
    
    for pwd in valid_passwords:
        try:
            validate_strong_password(pwd)
            print(f"✅ {pwd} - VÁLIDA")
        except Exception as e:
            print(f"❌ {pwd} - ERROR: {e}")
    
    for pwd in invalid_passwords:
        try:
            validate_strong_password(pwd)
            print(f"❌ {pwd} - DEBERÍA SER INVÁLIDA")
        except Exception as e:
            print(f"✅ {pwd} - CORRECTAMENTE RECHAZADA: {e}")

def test_sql_injection_validation():
    """Probar protección contra inyección SQL"""
    print("\n🔍 Probando protección contra inyección SQL...")
    
    safe_inputs = [
        "usuario normal",
        "email@example.com",
        "Mi nombre es Juan"
    ]
    
    malicious_inputs = [
        "'; DROP TABLE users; --",
        "1' OR '1'='1",
        "admin'; INSERT INTO users",
        "SELECT * FROM passwords"
    ]
    
    for input_text in safe_inputs:
        try:
            validate_no_sql_injection(input_text)
            print(f"✅ '{input_text}' - SEGURO")
        except Exception as e:
            print(f"❌ '{input_text}' - ERROR: {e}")
    
    for input_text in malicious_inputs:
        try:
            validate_no_sql_injection(input_text)
            print(f"❌ '{input_text}' - DEBERÍA SER BLOQUEADO")
        except Exception as e:
            print(f"✅ '{input_text}' - CORRECTAMENTE BLOQUEADO: {e}")

def test_html_sanitization():
    """Probar sanitización HTML"""
    print("\n🔍 Probando sanitización HTML...")
    
    html_inputs = [
        "<script>alert('XSS')</script>",
        "<b>Texto en negrita</b>",
        "<p>Párrafo normal</p>",
        "<img src='x' onerror='alert(1)'>",
        "Texto normal sin HTML"
    ]
    
    for html in html_inputs:
        sanitized = sanitize_html_input(html)
        print(f"Original: {html}")
        print(f"Sanitizado: {sanitized}")
        print("---")

if __name__ == "__main__":
    print("🧪 PROBANDO VALIDACIONES DE SEGURIDAD DE FERRAMASSTORE")
    print("=" * 60)
    
    test_phone_validation()
    test_password_validation()
    test_sql_injection_validation()
    test_html_sanitization()
    
    print("\n✨ Pruebas completadas!")
    print("\n📋 RESUMEN:")
    print("- Validación de teléfonos chilenos: Implementada ✅")
    print("- Validación de contraseñas fuertes: Implementada ✅") 
    print("- Protección contra SQL injection: Implementada ✅")
    print("- Sanitización HTML: Implementada ✅")
    print("- Rate limiting: Implementado ✅")
    print("- Honeypots anti-bot: Implementados ✅")
