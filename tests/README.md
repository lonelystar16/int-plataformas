# Estructura de Tests

Esta carpeta contiene todos los tests del proyecto organizados por categorías:

## 📁 Estructura de Carpetas

### `test_inventario/`
- `test_inventario_completo.py` - Tests completos de inventario
- `REPORTE_FINAL_INVENTARIO.md` - Reporte final de pruebas de inventario

### `test_security/`
- `test_security.py` - Tests de seguridad de la aplicación

### `test_urls/`
- `test_urls_django.py` - Tests de URLs de Django
- `test_urls_inventario.py` - Tests de URLs específicas del inventario

### `test_selenium/`
- `test_selenium_inventario.py` - Tests de Selenium para inventario

### `test_authentication/`
- `test_authentication.py` - Tests de autenticación y autorización

### `test_api/`
- `test_api_endpoints.py` - Tests de endpoints de API

### `test_integration/`
- `test_integration_complete.py` - Tests de integración completa

### `test_navigation/`
- `test_navigation.py` - Tests de navegación web

### `test_shopping_cart/`
- `test_shopping_cart.py` - Tests del carrito de compras

### `test_basic/`
- `test_basic.py` - Tests básicos de funcionalidad

## 📁 Carpetas Auxiliares

### `page_objects/`
- Contiene objetos de página para tests de Selenium

### `utils/`
- Utilidades y helpers para tests

## 🚀 Ejecutar Tests

Para ejecutar todos los tests:
```bash
python -m pytest tests/
```

Para ejecutar tests de una categoría específica:
```bash
python -m pytest tests/test_inventario/
python -m pytest tests/test_security/
python -m pytest tests/test_api/
# etc.
```

Para ejecutar un test específico:
```bash
python -m pytest tests/test_inventario/test_inventario_completo.py
```

## 📝 Notas

- Cada carpeta de test contiene un archivo `__init__.py` para que Python las reconozca como paquetes
- Los reportes y archivos de configuración relacionados están en sus respectivas carpetas
- Mantén esta estructura al agregar nuevos tests
