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

FerramasStore es una plataforma web para la gestión y visualización de productos y categorías de una ferretería, con funcionalidades de carrito de compras, autenticación de usuarios y una API RESTful para integración y administración.

## Descripción

El proyecto está desarrollado con Django y Django REST Framework, permitiendo:
- Visualización de productos por categorías.
- Carrito de compras persistente en el navegador.
- Registro e inicio de sesión de usuarios.
- Panel de administración para gestionar productos, categorías y usuarios.
- API RESTful para operaciones CRUD sobre productos y categorías.
- Sistema de descuentos para usuarios autenticados.
- Pop-up de suscripción a ofertas.
- Diseño responsivo con Tailwind CSS.

**Externalización de APIs:**  
Las funcionalidades relacionadas con productos, el valor del dólar (Banco Central de Chile) y Mercado Pago han sido externalizadas y funcionan mediante servidores independientes desarrollados con FASTAPI.  
Estas APIs externas son consumidas desde Django para integrar información adicional y mantener una arquitectura desacoplada y escalable.

## Estructura del Proyecto

- **app.domain.models**: Modelos de datos (`Producto`, `Categoria`, `Usuario`).
- **app.presentation.views**: Vistas para páginas web y endpoints de la API.
- **app.presentation.serializers**: Serializadores para la API REST.
- **app.presentation.urls** y **app.urls**: Rutas del sitio y de la API.
- **app/templates/pages/**: Templates HTML para las páginas del sitio.
- **app/templates/components/**: Componentes reutilizables (ej. carrito).
- **app/static/**: Archivos estáticos (CSS, JS, imágenes).
- **ferramas/urls.py**: Rutas principales del proyecto.

## Recursos utilizados

- **Python 3.10+**
- **Django 5.2.x**
- **Django REST Framework**
- **Tailwind CSS** (CDN)
- **SQLite** (por defecto, fácilmente migrable a PostgreSQL/MySQL)
- **HTML5, CSS3, JavaScript (ES6+)**
- **FASTAPI** (para las APIs externalizadas)
- **Uvicorn** (servidor ASGI para FASTAPI)
- **requests** (para consumo de APIs externas desde Django)
- **mercadopago** (SDK para integración de pagos)

## Requisitos para ejecutar el proyecto

- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- (Opcional) virtualenv para entornos virtuales
- **FASTAPI** y **Uvicorn** para levantar los servicios externalizados
- **requests** (instalar con `pip install requests`)

## Instalación y ejecución

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repo>
   cd int-plataformas
   ```

2. **Crear y activar un entorno virtual**
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Mac/Linux:
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install django djangorestframework mercadopago requests fastapi uvicorn selenium pytest pytest-html
   ```

4. **Migrar la base de datos**
   ```bash
   python manage.py migrate
   ```

5. **Crear un superusuario (opcional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Ejecutar el servidor**
   
   **Servidor Django**
   ```bash
   python manage.py runserver
   ```
   # En terminal separada
   **Servidor FastAPI**
   ```bash
   cd api
   uvicorn run:app --reload --port 8001
   ```

7. **Acceder a la aplicación**
   - Sitio web: [http://localhost:8000/](http://localhost:8000/)
   - API: [http://localhost:8000/api/](http://localhost:8000/api/)
   - Admin: [http://localhost:8000/admin/](http://localhost:8000/admin/)

## Funcionalidades principales

- **Catálogo de productos**: Visualización por categorías, stock, precios y descuentos. Los productos pueden provenir tanto de la base de datos local como de una API externa (FASTAPI).
- **Carrito de compras**: Añadir, quitar y modificar productos, resumen y total.
- **Autenticación**: Registro, inicio/cierre de sesión, descuentos para usuarios autenticados.
- **Panel de administración**: Gestión de productos, categorías y usuarios.
- **API RESTful**: Endpoints para productos y categorías, filtrado por categoría.
- **Pop-up de suscripción**: Para recibir ofertas semanales por correo.
- **Integración con Mercado Pago**: Pagos gestionados a través de una API externalizada.
- **Consulta del valor del dólar**: Consumo de la API del Banco Central de Chile externalizada vía FASTAPI.
- **Diseño responsivo**: Adaptado a dispositivos móviles y escritorio.

## Información de Pruebas 🧪

### Tipos de Pruebas Implementadas
- **Health Check y Documentación**: Verificación de conectividad de API, disponibilidad de documentación automática (Swagger UI, ReDoc, OpenAPI JSON).
- **CRUD de Productos y Categorías**: Listar, crear, y eliminar productos y categorías con validaciones y manejo de errores.
- **Servicios Externos**: Integración con APIs del Banco Central y Mercado Pago, validación de estructura de respuesta y manejo de errores de conectividad.
- **Performance**: Tiempo de respuesta, requests concurrentes y pruebas de estrés.
- **Manejo de Errores**: Endpoints inexistentes, métodos no permitidos, y JSON malformado.

### Herramientas y Tecnologías Utilizadas
- **Selenium WebDriver**: Automatización del navegador.
- **Pytest**: Framework de pruebas.
- **pytest-html**: Generación de reportes HTML interactivos.
- **Page Object Model**: Patrón de diseño para pruebas.
- **Pytest Fixtures**: Setup y teardown automático.

### Arquitectura de Pruebas
- **Base Test Class**: Configuración reutilizable para pruebas.
- **HTML Reports**: Reportes visuales con capturas de pantalla.

### Endpoints Probados
- **Banco Central**: `/banco-central/valor-dolar` (GET) - Obtener valor del dólar.
- **Mercado Pago**: `/mercado-pago/crear-pago` (POST) - Crear preferencia de pago.
- **Documentación API**: `/docs` (Swagger UI), `/redoc` (ReDoc), `/openapi.json` (Esquema OpenAPI).

### Estructura de Archivos de Pruebas
- **Configuración**:
  - `requirements-test.txt`: Dependencias para pruebas.
  - `pytest.ini`: Configuración de Pytest.
- **Reportes**:
  - `reports/`: Carpeta con reportes de pruebas en HTML y XML.
  - `test_session_*/`: Reportes generados por sesiones de prueba.

## Notas y recomendaciones

- Los templates HTML están en `app/templates/pages/` y los componentes reutilizables en `app/templates/components/`.
- Configura la variable `ALLOWED_HOSTS` en producción en `settings.py`.
- El idioma y zona horaria están configurados para Chile (`es-cl`, `America/Santiago`).
- Puedes migrar fácilmente a otra base de datos editando la sección `DATABASES` en `settings.py`.
- Para desarrollo, el modo `DEBUG` está activado. Desactívalo en producción.
- El sistema de usuarios extiende el modelo de Django con el modelo `Usuario` para almacenar teléfono.

## Créditos

Desarrollado por el equipo de FerramasStore para la asignatura de Integración de Plataformas.

---
