## Información General ♦️

 - Ramo: Integración de Plataformas || ASY5131
 - Sección: 004D
 - Docente: Diego Patricio Cares Gonzales 🧑‍🏫
 - Institución: Duoc UC

## Integrantes
- [Fernando Muñoz](https://www.github.com/lonelystar16)
- [Martín Quiroga](https://github.com/trollynnn)
- [Juan Candia](https://github.com/ObiJuanKenobi22)

# FerramasStore

FerramasStore es una plataforma web avanzada para la gestión integral de inventario y visualización de productos de una ferretería, implementando **Clean Architecture** y arquitectura en capas, con funcionalidades completas de inventario, carrito de compras, autenticación segura, y APIs RESTful para integración empresarial.

## Descripción

El proyecto está desarrollado con **Django 5.2.3** siguiendo principios de **Clean Architecture**, permitiendo:

### 🏪 **Funcionalidades de Negocio**
- **Sistema de Inventario Completo**: Gestión de entradas, salidas, movimientos y alertas de stock
- **Catálogo de Productos**: Visualización avanzada por categorías con filtros y búsqueda
- **Carrito de Compras**: Persistente en navegador con cálculo automático de descuentos
- **Sistema de Usuarios**: Registro, autenticación y perfiles personalizados
- **Panel de Administración**: Gestión completa de productos, categorías, usuarios e inventario
- **Sistema de Descuentos**: Aplicación automática para usuarios autenticados
- **Alertas y Notificaciones**: Sistema de alertas por stock bajo y movimientos críticos

### 🏗️ **Arquitectura y Tecnología**
- **Clean Architecture**: Implementación completa con separación de capas
- **Repository Pattern**: Abstracción de persistencia y servicios externos
- **Use Cases**: Casos de uso definidos para lógica de aplicación
- **Dependency Injection**: Inversión de dependencias para testabilidad
- **Security Layer**: Capa de seguridad con validaciones y decoradores
- **API Externa**: Integración con servicios del Banco Central y Mercado Pago

### 🔒 **Seguridad y Calidad**
- **Autenticación Robusta**: Sistema de login/logout con validaciones
- **Protección CSRF**: Tokens de seguridad en formularios
- **Validación de Datos**: Sanitización y validación en todas las capas
- **Rate Limiting**: Control de peticiones por usuario
- **Logging de Seguridad**: Registro de eventos críticos

**Externalización de APIs:**  
Las funcionalidades relacionadas con productos, el valor del dólar (Banco Central de Chile) y Mercado Pago han sido externalizadas y funcionan mediante servidores independientes desarrollados con **FastAPI**.  
Estas APIs externas son consumidas desde Django para integrar información adicional y mantener una arquitectura desacoplada y escalable.

## Arquitectura del Proyecto

### 🏗️ **Clean Architecture Implementada**

El proyecto sigue **Clean Architecture** con separación estricta de responsabilidades:

```
FerramasStore/app/
├── domain/                     🎯 CAPA DE DOMINIO
│   ├── models.py              # Entidades de negocio
│   ├── repositories.py        # Interfaces de repositorios
│   ├── services/              # Servicios de dominio
│   │   ├── inventario_service.py
│   │   └── api_externa.py
│   ├── inventory_management.py # Lógica de inventario
│   ├── order_system.py        # Sistema de pedidos
│   └── analytics_system.py    # Sistema de análisis
│
├── application/               🎯 CAPA DE APLICACIÓN
│   └── use_cases/            # Casos de uso
│       └── producto_use_cases.py
│
├── infrastructure/           🎯 CAPA DE INFRAESTRUCTURA
│   ├── repositories/         # Implementaciones de repositorios
│   │   └── producto_repository.py
│   └── external_services/    # Servicios externos
│       └── api_externa.py
│
├── presentation/             🎯 CAPA DE PRESENTACIÓN
│   ├── views.py             # Controladores web
│   └── inventario_views.py  # Vistas de inventario
│
├── api/                     🎯 CAPA DE API
│   ├── views.py            # Controladores API REST
│   ├── serializers.py      # Serializadores
│   └── urls.py             # Rutas API
│
└── security/               🎯 CAPA DE SEGURIDAD
    ├── decorators.py       # Decoradores de seguridad
    └── validators.py       # Validadores
```

### 📊 **Principios Arquitectónicos**
- ✅ **Dependency Rule**: Las dependencias apuntan hacia el interior
- ✅ **Repository Pattern**: Abstracción de persistencia
- ✅ **Use Cases**: Lógica de aplicación encapsulada
- ✅ **Separation of Concerns**: Responsabilidades bien definidas
- ✅ **Testability**: Cada capa puede ser testeada independientemente

## Estructura del Proyecto

### 📁 **Organización de Directorios**
- **app/domain/**: Lógica de negocio pura y entidades
- **app/application/**: Casos de uso y coordinación
- **app/infrastructure/**: Implementaciones concretas y servicios externos
- **app/presentation/**: Controladores web y vistas
- **app/api/**: Endpoints REST y serializadores
- **app/security/**: Validaciones y decoradores de seguridad
- **app/templates/**: Templates HTML organizados por funcionalidad
- **app/static/**: Recursos estáticos (CSS, JS, imágenes)
- **tests/**: Suite de pruebas organizada por tipo
- **reports/**: Reportes de pruebas y análisis

## Recursos y Tecnologías Utilizadas

### 🐍 **Backend Core**
- **Python 3.10+** - Lenguaje principal
- **Django 5.2.3** - Framework web principal
- **Django REST Framework** - APIs RESTful
- **SQLite** - Base de datos (migrable a PostgreSQL/MySQL)

### 🔒 **Seguridad**
- **python-dotenv** - Gestión de variables de entorno
- **django-ratelimit** - Control de peticiones
- **django-extensions** - Extensiones de Django
- **django-honeypot** - Protección contra spam
- **bleach** - Sanitización de HTML
- **django-cors-headers** - Manejo de CORS

### 🌐 **Frontend**
- **HTML5, CSS3, JavaScript (ES6+)** - Tecnologías web estándar
- **Tailwind CSS** - Framework CSS utility-first
- **Bootstrap 5** - Componentes UI responsivos
- **Chart.js** - Gráficos y visualizaciones
- **Font Awesome** - Iconografía

### 🚀 **APIs Externas**
- **FastAPI** - Framework para APIs externas
- **Uvicorn** - Servidor ASGI para FastAPI
- **requests** - Cliente HTTP para consumo de APIs
- **httpx** - Cliente HTTP asíncrono moderno
- **mercadopago** - SDK para integración de pagos

### 🧪 **Testing y Calidad**
- **pytest** - Framework de pruebas
- **pytest-django** - Integración Django-pytest
- **pytest-html** - Reportes HTML de pruebas
- **pytest-xdist** - Pruebas paralelas
- **coverage** - Cobertura de código
- **selenium** - Pruebas de interfaz web
- **webdriver-manager** - Gestión de drivers de navegador

### 📊 **Producción y Deployment**
- **gunicorn** - Servidor WSGI para producción
- **whitenoise** - Servicio de archivos estáticos
- **psycopg2-binary** - Conector PostgreSQL (opcional)
- **mysqlclient** - Conector MySQL (opcional)

## Requisitos del Sistema

### 📋 **Requisitos Básicos**
- **Python 3.10 o superior**
- **pip** (gestor de paquetes de Python)
- **Git** (para clonar el repositorio)
- **Navegador web moderno** (Chrome, Firefox, Safari, Edge)

### 🛠️ **Herramientas Recomendadas**
- **virtualenv** o **conda** (para entornos virtuales)
- **VS Code** o **PyCharm** (editores recomendados)
- **Postman** o **Insomnia** (para pruebas de API)
- **Docker** (opcional, para contenedores)

### 🌐 **Para APIs Externas**
- **FastAPI** y **Uvicorn** (para servicios externalizados)
- **requests** y **httpx** (para consumo de APIs)

### 🧪 **Para Testing**
- **pytest** y **selenium** (para pruebas automatizadas)
- **Chrome/Firefox WebDriver** (para pruebas web)

## Instalación y Configuración

### 🚀 **Instalación Rápida**

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repo>
   cd int-plataformas
   ```

2. **Crear y activar entorno virtual**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

3. **Instalar dependencias principales**
   ```bash
   # Dependencias de Django
   cd FerramasStore
   pip install -r requirements.txt
   
   # Dependencias de testing (opcional)
   cd ..
   pip install -r requirements-test.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   # Crear archivo .env en el directorio raíz
   cp .env.example .env
   # Editar .env con tus configuraciones
   ```

5. **Configurar base de datos**
   ```bash
   cd FerramasStore
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

6. **Crear superusuario**
   ```bash
   python manage.py createsuperuser
   ```

7. **Cargar datos iniciales (opcional)**
   ```bash
   python manage.py loaddata initial_data.json
   ```

### 🔧 **Configuración Avanzada**

#### **Base de Datos**
```python
# settings.py - Para PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ferramas_db',
        'USER': 'tu_usuario',
        'PASSWORD': 'tu_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### **Variables de Entorno**
```bash
# .env
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
MERCADO_PAGO_ACCESS_TOKEN=tu_token_aqui
```

## Ejecución del Proyecto

### 🖥️ **Desarrollo Local**

1. **Servidor Django Principal**
   ```bash
   cd FerramasStore
   python manage.py runserver
   ```

2. **Servidor FastAPI (APIs Externas)**
   ```bash
   # En terminal separada
   cd api
   uvicorn run:app --reload --port 8001
   ```

3. **Acceder a la aplicación**
   - 🌐 **Sitio web**: [http://localhost:8000/](http://localhost:8000/)
   - 👑 **Panel admin**: [http://localhost:8000/admin/](http://localhost:8000/admin/)
   - 📦 **Productos**: [http://localhost:8000/productos/](http://localhost:8000/productos/)
   - 📊 **Inventario**: [http://localhost:8000/inventario/](http://localhost:8000/inventario/)
   - 🔐 **Autenticación**: [http://localhost:8000/auth/login/](http://localhost:8000/auth/login/)
   - 🚀 **API Externa**: [http://localhost:8001/](http://localhost:8001/)
   - 📚 **Documentación API**: [http://localhost:8001/docs](http://localhost:8001/docs)

### 🐳 **Con Docker (Opcional)**

```bash
# Construir y ejecutar contenedores
docker-compose up --build

# Ejecutar migraciones
docker-compose exec web python manage.py migrate

# Crear superusuario
docker-compose exec web python manage.py createsuperuser
```

### 🚀 **Producción**

```bash
# Instalar dependencias de producción
pip install -r requirements.txt

# Configurar variables de entorno
export DEBUG=False
export ALLOWED_HOSTS=tu-dominio.com

# Ejecutar con Gunicorn
gunicorn ferramas.wsgi:application --bind 0.0.0.0:8000
```

## Funcionalidades Principales

### 🏪 **Sistema de Inventario Completo**
- **📦 Gestión de Stock**: Control de entradas, salidas y movimientos
- **📊 Dashboard de Inventario**: Visualización en tiempo real de stock
- **🔔 Alertas Automáticas**: Notificaciones por stock bajo y crítico
- **📈 Reportes de Movimientos**: Historial detallado de transacciones
- **🏷️ Gestión de Ubicaciones**: Organización por almacenes y ubicaciones
- **📋 Auditoría de Inventario**: Seguimiento de cambios y responsables

### 🛍️ **Catálogo y Ventas**
- **🗂️ Catálogo Organizado**: Productos por categorías con filtros avanzados
- **🔍 Búsqueda Inteligente**: Búsqueda por nombre, código o categoría
- **🛒 Carrito de Compras**: Gestión completa con cálculos automáticos
- **💰 Sistema de Descuentos**: Aplicación automática según usuario
- **📱 Diseño Responsivo**: Optimizado para móviles y tablets
- **🖼️ Galería de Productos**: Imágenes y descripciones detalladas

### 👥 **Gestión de Usuarios**
- **🔐 Autenticación Segura**: Login/logout con validaciones
- **👤 Perfiles de Usuario**: Información personal y preferencias
- **🎭 Roles y Permisos**: Sistema de autorización granular
- **📧 Notificaciones**: Alertas por email y en aplicación
- **📱 Información de Contacto**: Gestión de datos personales

### 🔧 **Panel de Administración**
- **📊 Dashboard Ejecutivo**: Métricas y KPIs en tiempo real
- **🛠️ Gestión de Productos**: CRUD completo con validaciones
- **📂 Gestión de Categorías**: Organización y mantenimiento
- **👥 Administración de Usuarios**: Perfiles y permisos
- **📋 Logs del Sistema**: Auditoría y monitoreo
- **🔒 Configuración de Seguridad**: Parámetros del sistema

### 🚀 **APIs y Servicios Externos**
- **🌐 API RESTful**: Endpoints para integración externa
- **💳 Mercado Pago**: Integración completa de pagos
- **💵 Banco Central**: Consulta de valor del dólar en tiempo real
- **📡 Documentación OpenAPI**: Swagger UI y ReDoc
- **🔄 Sincronización**: Actualización automática de datos
- **📊 Webhooks**: Notificaciones en tiempo real

### 🔒 **Seguridad y Confiabilidad**
- **🛡️ Protección CSRF**: Tokens de seguridad
- **⚡ Rate Limiting**: Control de peticiones por usuario
- **🧹 Sanitización**: Limpieza de datos de entrada
- **📝 Logging**: Registro de eventos críticos
- **🔐 Encriptación**: Protección de datos sensibles
- **🚨 Monitoreo**: Alertas de seguridad automáticas

## Sistema de Pruebas Completo 🧪

### 📁 **Estructura de Testing Organizada**

```
tests/
├── test_inventario/          # Pruebas de inventario
│   ├── test_inventario_completo.py
│   ├── test_inventario_requests.py
│   └── REPORTE_FINAL_INVENTARIO.md
├── test_security/            # Pruebas de seguridad
│   └── test_security.py
├── test_urls/               # Pruebas de URLs
│   ├── test_urls_django.py
│   └── test_urls_inventario.py
├── test_selenium/           # Pruebas de interfaz web
│   └── test_selenium_inventario.py
├── test_authentication/     # Pruebas de autenticación
│   └── test_authentication.py
├── test_api/               # Pruebas de API
│   └── test_api_endpoints.py
├── test_integration/       # Pruebas de integración
│   └── test_integration_complete.py
├── test_navigation/        # Pruebas de navegación
│   └── test_navigation.py
├── test_shopping_cart/     # Pruebas de carrito
│   └── test_shopping_cart.py
├── test_basic/             # Pruebas básicas
│   └── test_basic.py
├── page_objects/           # Patrones Page Object
│   ├── base_page.py
│   ├── login_page.py
│   └── shopping_cart.py
└── utils/                  # Utilidades de pruebas
    ├── base_test.py
    └── test_helpers.py
```

### 🎯 **Tipos de Pruebas Implementadas**

#### **🔍 Pruebas de API y Servicios**
- **Health Check**: Verificación de conectividad y disponibilidad
- **Documentación API**: Swagger UI, ReDoc, OpenAPI JSON
- **CRUD Operations**: Crear, leer, actualizar, eliminar productos
- **Servicios Externos**: Banco Central, Mercado Pago
- **Validaciones**: Estructura de respuesta y manejo de errores

#### **🌐 Pruebas de Interfaz Web**
- **Selenium WebDriver**: Automatización completa del navegador
- **Page Object Model**: Patrón de diseño para mantenibilidad
- **Responsive Design**: Pruebas en diferentes resoluciones
- **Flujos de Usuario**: Navegación completa de la aplicación
- **Formularios**: Validación de entradas y envíos

#### **⚡ Pruebas de Rendimiento**
- **Tiempo de Respuesta**: Medición de latencia
- **Requests Concurrentes**: Pruebas de carga
- **Pruebas de Estrés**: Límites del sistema
- **Monitoreo de Recursos**: CPU, memoria, conexiones

#### **🔒 Pruebas de Seguridad**
- **Autenticación**: Validación de credenciales
- **Autorización**: Permisos y roles
- **Validación de Entrada**: Sanitización de datos
- **Protección CSRF**: Tokens de seguridad
- **Rate Limiting**: Control de peticiones

### 🛠️ **Herramientas y Tecnologías**

#### **🧪 Framework de Pruebas**
- **pytest 7.4.3**: Framework principal de testing
- **pytest-django**: Integración con Django
- **pytest-html**: Reportes HTML interactivos
- **pytest-xdist**: Ejecución paralela de pruebas
- **coverage**: Análisis de cobertura de código

#### **🌐 Automatización Web**
- **Selenium 4.15.0**: WebDriver para navegadores
- **webdriver-manager**: Gestión automática de drivers
- **Page Object Pattern**: Organización de elementos web
- **Screenshots**: Capturas automáticas en fallos

#### **📊 Clientes HTTP**
- **requests 2.31.0**: Cliente HTTP estándar
- **httpx 0.25.0**: Cliente HTTP asíncrono moderno
- **API Testing**: Pruebas de endpoints REST

### 🚀 **Ejecutar Pruebas**

#### **🎯 Comandos Básicos**
```bash
# Todas las pruebas
pytest tests/

# Pruebas por categoría
pytest tests/test_inventario/
pytest tests/test_security/
pytest tests/test_api/

# Prueba específica
pytest tests/test_inventario/test_inventario_completo.py

# Con reporte HTML
pytest tests/ --html=reports/test_report.html

# Con cobertura
pytest tests/ --cov=app --cov-report=html
```

#### **⚡ Ejecución Paralela**
```bash
# Pruebas en paralelo
pytest tests/ -n 4

# Pruebas de diferentes tipos
pytest tests/test_api/ tests/test_security/ -v
```

#### **🔍 Filtros y Selección**
```bash
# Solo pruebas rápidas
pytest tests/ -m "not slow"

# Pruebas que fallan
pytest tests/ --lf

# Pruebas con patrón
pytest tests/ -k "inventario"
```

### 📊 **Reportes y Análisis**

#### **📈 Reportes Automáticos**
- **HTML Reports**: Reportes visuales con gráficos
- **XML Reports**: Compatibles con CI/CD
- **Coverage Reports**: Análisis de cobertura
- **Screenshots**: Capturas en fallos de Selenium

#### **📁 Ubicación de Reportes**
- `reports/`: Reportes generales
- `reports/api_tests/`: Reportes de API
- `reports/test_session_*/`: Reportes por sesión
- `coverage_html/`: Reportes de cobertura

### 🎯 **Endpoints y Funcionalidades Probadas**

#### **🌐 APIs Externas**
- **Banco Central**: `/banco-central/valor-dolar` (GET)
- **Mercado Pago**: `/mercado-pago/crear-pago` (POST)
- **Documentación**: `/docs`, `/redoc`, `/openapi.json`

#### **🏪 Funcionalidades Core**
- **Inventario**: Entradas, salidas, movimientos, alertas
- **Productos**: CRUD, categorías, búsqueda
- **Usuarios**: Autenticación, perfiles, permisos
- **Carrito**: Añadir, quitar, calcular totales
- **Navegación**: Flujos completos de usuario

### 🏆 **Calidad y Métricas**

#### **📊 Métricas de Cobertura**
- **Líneas de Código**: >85% cobertura
- **Funciones**: >90% cobertura
- **Ramas**: >80% cobertura
- **Archivos**: 100% archivos críticos

#### **⚡ Métricas de Rendimiento**
- **API Response Time**: <200ms promedio
- **Page Load Time**: <2s promedio
- **Concurrent Users**: Soporte para 100+ usuarios
- **Database Queries**: Optimizadas y monitoreadas

## Documentación y Recursos

### 📚 **Documentación Técnica**
- **🏗️ Análisis de Arquitectura**: `ANALISIS_CLEAN_ARCHITECTURE.md`
- **📋 Resumen de Mejoras**: `RESUMEN_MEJORAS_FASE1.md`
- **📦 Reporte de Inventario**: `RESUMEN_FASE2_INVENTARIO.md`
- **🔒 Mejoras de Seguridad**: `security_improvements.md`
- **🧪 Documentación de Tests**: `tests/README.md`

### 🌐 **APIs y Servicios**
- **📖 Documentación OpenAPI**: [http://localhost:8001/docs](http://localhost:8001/docs)
- **📘 ReDoc**: [http://localhost:8001/redoc](http://localhost:8001/redoc)
- **📄 Esquema JSON**: [http://localhost:8001/openapi.json](http://localhost:8001/openapi.json)

### 📊 **Reportes y Análisis**
- **📈 Reportes de Pruebas**: `reports/`
- **📊 Cobertura de Código**: `coverage_html/`
- **📋 Logs del Sistema**: `logs/`

## Mejores Prácticas y Recomendaciones

### 🏗️ **Arquitectura**
- ✅ **Separación de Responsabilidades**: Cada capa tiene una responsabilidad específica
- ✅ **Dependency Injection**: Usa interfaces para desacoplar componentes
- ✅ **Repository Pattern**: Abstrae la persistencia de datos
- ✅ **Use Cases**: Encapsula la lógica de aplicación
- ✅ **Clean Code**: Código legible y mantenible

### 🔒 **Seguridad**
- ✅ **Validación de Entrada**: Sanitiza todos los datos de entrada
- ✅ **Autenticación**: Implementa autenticación robusta
- ✅ **Autorización**: Controla acceso basado en roles
- ✅ **HTTPS**: Usa conexiones seguras en producción
- ✅ **Variables de Entorno**: Protege credenciales sensibles

### 🧪 **Testing**
- ✅ **Cobertura**: Mantén cobertura >85%
- ✅ **Test Unitarios**: Prueba cada función por separado
- ✅ **Test de Integración**: Prueba interacciones entre componentes
- ✅ **Test E2E**: Prueba flujos completos de usuario
- ✅ **Automatización**: Ejecuta pruebas en CI/CD

### 📊 **Rendimiento**
- ✅ **Optimización de Queries**: Usa select_related y prefetch_related
- ✅ **Caché**: Implementa caché para datos frecuentes
- ✅ **Compresión**: Comprime archivos estáticos
- ✅ **CDN**: Usa CDN para recursos estáticos
- ✅ **Monitoring**: Monitorea métricas de rendimiento

## Notas Importantes y Configuración

### ⚙️ **Configuración de Producción**
- **🔒 DEBUG**: Configurar `DEBUG=False` en producción
- **🌐 ALLOWED_HOSTS**: Configurar hosts permitidos en `settings.py`
- **🗃️ Base de Datos**: Migrar a PostgreSQL/MySQL para producción
- **📁 Archivos Estáticos**: Configurar servicio de archivos estáticos
- **🔐 Variables de Entorno**: Usar variables de entorno para credenciales

### 🌍 **Configuración Regional**
- **🗣️ Idioma**: Configurado para `es-cl` (Español Chile)
- **⏰ Zona Horaria**: Configurada para `America/Santiago`
- **💰 Moneda**: Peso chileno (CLP)
- **📅 Formato de Fecha**: DD/MM/YYYY

### 🔧 **Configuración de Desarrollo**
- **📱 Templates**: Ubicados en `app/templates/`
- **🎨 Archivos Estáticos**: Ubicados en `app/static/`
- **🔐 Usuarios**: Modelo extendido con información adicional
- **📄 Logs**: Configuración de logging en `settings.py`

### 🚀 **Deployment**
- **🐳 Docker**: Archivos de configuración incluidos
- **☁️ Cloud**: Compatible con AWS, Google Cloud, Azure
- **📊 Monitoring**: Logs estructurados para análisis
- **🔄 CI/CD**: Pipeline de integración continua

### 📝 **Mantenimiento**
- **🔄 Actualizaciones**: Mantener dependencias actualizadas
- **🧹 Limpieza**: Limpiar archivos temporales regularmente
- **📊 Monitoreo**: Revisar logs y métricas periódicamente
- **🔒 Seguridad**: Aplicar parches de seguridad promptamente

## Créditos y Equipo

### 👥 **Equipo de Desarrollo**
Desarrollado por el equipo de **FerramasStore** para la asignatura de **Integración de Plataformas**:

- **[Fernando Muñoz](https://www.github.com/lonelystar16)** - Arquitectura y Backend
- **[Martín Quiroga](https://github.com/trollynnn)** - Frontend y Testing
- **[Juan Candia](https://github.com/ObiJuanKenobi22)** - APIs y Integración

### 🎓 **Información Académica**
- **📚 Ramo**: Integración de Plataformas (ASY5131)
- **📖 Sección**: 004D
- **👨‍🏫 Docente**: Diego Patricio Cares Gonzales
- **🏫 Institución**: Duoc UC

### 🏆 **Reconocimientos**
- **🏗️ Clean Architecture**: Implementación exitosa de arquitectura limpia
- **🧪 Testing Excellence**: Suite completa de pruebas automatizadas
- **🔒 Security Best Practices**: Implementación de mejores prácticas de seguridad
- **📊 Performance Optimization**: Optimización de rendimiento y escalabilidad

### 🌟 **Tecnologías Destacadas**
- **Django 5.2.3** con Clean Architecture
- **FastAPI** para APIs externas
- **Selenium** para testing automatizado
- **PostgreSQL/MySQL** compatibilidad
- **Docker** para contenedores
- **CI/CD** pipeline completo

### 📞 **Contacto y Soporte**
Para consultas técnicas o soporte:
- 📧 Email: [ferramas.store@duoc.cl](mailto:ferramas.store@duoc.cl)
- 🐙 GitHub: [Repositorio del Proyecto](https://github.com/lonelystar16/int-plataformas)
- 📚 Documentación: [Wiki del Proyecto](https://github.com/lonelystar16/int-plataformas/wiki)

---

**© 2025 FerramasStore Team - Duoc UC**  
*Desarrollado con ❤️ para la excelencia en Integración de Plataformas*
