# Generated by Django 5.2.3 on 2025-06-30 20:30

from django.db import migrations





def poblar_productos(apps, schema_editor):
    Producto = apps.get_model('app', 'Producto')
    Categoria = apps.get_model('app', 'Categoria')

    # Productos de ejemplo
    productos_a_crear = [
        {
            'nombre': 'Martillo',
            'precio': 15000,
            'stock': 100,
            'descripcion': 'Martillo de acero forjado, ideal para trabajos de construcción.',
            'categoria': 'Herramientas Manuales',
        },
        {
            'nombre': 'Taladro',
            'precio': 120000,
            'stock': 50,
            'descripcion': 'Taladro eléctrico con velocidad variable, perfecto para perforar madera y metal.',
            'categoria': 'Herramientas Manuales',
        },
        {
            'nombre': 'Guantes de Seguridad',
            'precio': 5000,
            'stock': 200,
            'descripcion': 'Guantes resistentes al corte, ideales para trabajos de construcción y jardinería.',
            'categoria': 'Equipos de Seguridad',
        },
        {
            'nombre': 'Tornillos de Anclaje',
            'precio': 3000,
            'stock': 500,
            'descripcion': 'Tornillos de anclaje para fijación en concreto, acero inoxidable.',
            'categoria': 'Tornillos y Anclajes',
        },
        {
            'nombre': 'Cinta Métrica',
            'precio': 8000,
            'stock': 150,
            'descripcion': 'Cinta métrica de 5 metros, con bloqueo automático y gancho magnético.',
            'categoria': 'Equipos de Medición',
        },
    ]

    for datos_producto in productos_a_crear:
        # Buscamos la categoría
        try:
            categoria_obj = Categoria.objects.get(nombre=datos_producto['categoria'])
            # Creamos el producto asociado a la categoría
            Producto.objects.create(
                nombre=datos_producto["nombre"],
                precio=datos_producto["precio"],
                stock=datos_producto["stock"],
                descripcion=datos_producto["descripcion"],
                categoria=categoria_obj
            )
        except Categoria.DoesNotExist:
            print(f"Categoría '{datos_producto['categoria']}' no encontrada. Producto '{datos_producto['nombre']}' no creado.")
        





class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_crear_categorias_iniciales'),
    ]

    operations = [
    ]
