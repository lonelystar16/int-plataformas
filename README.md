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
   pip install django djangorestframework mercadopago requests fastapi uvicorn
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
   python run.py
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
