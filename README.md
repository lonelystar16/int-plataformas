# FerramasStore

Proyecto de plataforma web para la gestión y visualización de productos y categorías de una ferretería.

## Descripción

Este proyecto utiliza Django y Django REST Framework para crear una API y un sitio web que permite visualizar y administrar productos y categorías. Incluye vistas para páginas informativas y endpoints para la gestión vía API.

## Estructura

- **app.domain.models**: Modelos de Producto y Categoría.
- **app.presentation.views**: Vistas para páginas web y API.
- **app.presentation.serializers**: Serializadores para la API.
- **app.urls**: Rutas del sitio y de la API.
- **ferramas.urls**: Rutas principales del proyecto.

## Recursos utilizados

- Python 3.10+
- Django 5.2.x
- Django REST Framework

## Instalación y ejecución en otro entorno

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repo>
   cd int-plataformas
   ```

2. **Crear y activar un entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install django djangorestframework
   ```

4. **Migrar la base de datos**
   ```bash
   python manage.py migrate
   ```

5. **Crear un superusuario (opcional)
   ```bash
   python manage.py createsuperuser
   ```

6. **Ejecutar el servidor**
   ```bash
   python manage.py runserver
   ```

7. **Acceder a la aplicación**
   - Sitio web: [http://localhost:8000/](http://localhost:8000/)
   - API: [http://localhost:8000/api/](http://localhost:8000/api/)
   - Admin: [http://localhost:8000/admin/](http://localhost:8000/admin/)

## Notas

- Los templates HTML deben estar en `app/templates/pages/`.
- Configura la variable `ALLOWED_HOSTS` en producción.
- El archivo `settings.py` ya está configurado para español y zona horaria de Santiago.

---
