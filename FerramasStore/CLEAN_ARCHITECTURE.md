# Arquitectura Clean Architecture - FerramasStore

Este proyecto sigue los principios de **Clean Architecture** para mantener el código organizad, testeable y mantenible.

## Estructura de Capas

```
app/
├── domain/                    # Capa de Dominio (Entidades y Reglas de Negocio)
│   ├── models.py              # Entidades del dominio
│   ├── repositories.py        # Interfaces de repositorios
│   └── services/              # Servicios del dominio
│
├── application/               # Capa de Aplicación (Casos de Uso)
│   └── use_cases/
│       └── producto_use_cases.py  # Casos de uso de productos
│
├── infrastructure/           # Capa de Infraestructura (Implementaciones concretas)
│   ├── repositories/
│   │   └── producto_repository.py  # Implementación de repositorios
│   └── external_services/
│       └── api_externa.py     # Servicios externos (APIs, etc.)
│
├── presentation/             # Capa de Presentación (Controladores, Vistas, APIs)
│   ├── views.py              # Vistas Django
│   ├── serializers.py        # Serializers DRF
│   ├── urls.py               # URLs de la aplicación
│   └── admin.py              # Configuración del admin
│
├── static/                   # Archivos estáticos
├── templates/                # Templates HTML
├── migrations/               # Migraciones de Django
└── tests/                    # Tests
```

## Principios de Clean Architecture

### 1. **Capa de Dominio** (`domain/`)
- **Responsabilidad**: Contiene las entidades, reglas de negocio y lógica core
- **Dependencias**: No depende de ninguna otra capa
- **Contenido**:
  - `models.py`: Entidades del dominio (Usuario, Producto, Categoria, etc.)
  - `repositories.py`: Interfaces/contratos para acceso a datos
  - `services/`: Servicios del dominio

### 2. **Capa de Aplicación** (`application/`)
- **Responsabilidad**: Casos de uso y orquestación de la lógica de negocio
- **Dependencias**: Solo depende de la capa de dominio
- **Contenido**:
  - `use_cases/`: Casos de uso específicos (GetProductosPorCategoria, CreateProducto, etc.)

### 3. **Capa de Infraestructura** (`infrastructure/`)
- **Responsabilidad**: Implementaciones concretas de interfaces del dominio
- **Dependencias**: Depende de domain y application
- **Contenido**:
  - `repositories/`: Implementaciones concretas de repositorios (usando Django ORM)
  - `external_services/`: Servicios externos (APIs, sistemas de pago, etc.)

### 4. **Capa de Presentación** (`presentation/`)
- **Responsabilidad**: Interfaz de usuario, APIs REST, controladores web
- **Dependencias**: Depende de todas las otras capas
- **Contenido**:
  - `views.py`: Vistas Django y ViewSets DRF
  - `serializers.py`: Serializers para la API REST
  - `urls.py`: Configuración de rutas
  - `admin.py`: Configuración del panel de administración

## Flujo de Datos

```
Request → Presentation → Application (Use Cases) → Domain ← Infrastructure
                ↑                                              ↓
              Response ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ←
```

## Ejemplo de Uso

### Obtener productos por categoría:

1. **Presentation**: `herra_manuales(request)` recibe la petición
2. **Application**: `GetProductosPorCategoriaUseCase` ejecuta la lógica
3. **Infrastructure**: `DjangoProductoRepository` accede a la base de datos
4. **Domain**: Entidades `Producto` y `Categoria` representan los datos

```python
# 1. Presentation Layer (views.py)
def herra_manuales(request):
    productos, error = get_productos_por_categoria_use_case.execute("Herramientas Manuales")
    # ...

# 2. Application Layer (use_cases.py)
class GetProductosPorCategoriaUseCase:
    def execute(self, categoria_nombre: str):
        categoria = self.categoria_repository.get_by_name(categoria_nombre)
        productos = self.producto_repository.get_by_categoria(categoria)
        # ...

# 3. Infrastructure Layer (repositories.py)
class DjangoProductoRepository:
    def get_by_categoria(self, categoria, en_venta=True):
        return Producto.objects.filter(categoria=categoria, en_venta=en_venta)
```

## Beneficios

✅ **Testabilidad**: Cada capa puede ser testeada independientemente
✅ **Mantenibilidad**: Cambios en una capa no afectan otras
✅ **Flexibilidad**: Fácil cambio de tecnologías (ej: cambiar Django por FastAPI)
✅ **Separación de responsabilidades**: Cada capa tiene una responsabilidad clara
✅ **Inversión de dependencias**: Las capas internas no conocen las externas

## Archivos de Django en la raíz

Los siguientes archivos en la raíz de `app/` son requeridos por Django y solo importan desde las capas correspondientes:

- `models.py` → Importa desde `domain/models.py`
- `admin.py` → Importa desde `presentation/admin.py`
- `views.py` → **DEPRECATED** - Usar `presentation/views.py`
- `urls.py` → **DEPRECATED** - Usar `presentation/urls.py`
