from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.domain.models import (
    Proveedor, Ubicacion, Producto, Categoria, 
    ConfiguracionInventario, LoteInventario
)
from app.domain.services.inventario_service import InventarioService
from decimal import Decimal

class Command(BaseCommand):
    help = 'Inicializa datos de ejemplo para el sistema de inventario'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Inicializando datos de inventario...')

        # Crear superusuario si no existe
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@ferramas.cl',
                password='admin123'
            )
            self.stdout.write(f'✅ Superusuario creado: admin / admin123')
        else:
            admin_user = User.objects.get(username='admin')

        # Crear proveedores
        proveedores_data = [
            {
                'nombre': 'Ferretería Nacional SpA',
                'rut': '12345678-9',
                'email': 'ventas@ferrenacional.cl',
                'telefono': '+56912345678',
                'direccion': 'Av. Industrial 123, Santiago',
                'contacto_principal': 'Juan Pérez',
                'condicion_pago': '30 días',
                'descuento_proveedor': Decimal('5.00'),
            },
            {
                'nombre': 'Distribuidora Herramientas Ltda',
                'rut': '87654321-0',
                'email': 'compras@distherra.cl',
                'telefono': '+56987654321',
                'direccion': 'Calle Los Artesanos 456, Valparaíso',
                'contacto_principal': 'María González',
                'condicion_pago': '15 días',
                'descuento_proveedor': Decimal('3.50'),
            },
            {
                'nombre': 'Importadora Tornillos Chile',
                'rut': '11223344-5',
                'email': 'info@tornilloschile.cl',
                'telefono': '+56911223344',
                'direccion': 'Av. Libertador 789, Concepción',
                'contacto_principal': 'Carlos Rodríguez',
                'condicion_pago': '45 días',
                'descuento_proveedor': Decimal('7.00'),
            }
        ]

        for proveedor_data in proveedores_data:
            proveedor, created = Proveedor.objects.get_or_create(
                rut=proveedor_data['rut'],
                defaults=proveedor_data
            )
            if created:
                self.stdout.write(f'✅ Proveedor creado: {proveedor.nombre}')

        # Crear ubicaciones
        ubicaciones_data = [
            {
                'codigo': 'BOD-A1-001',
                'nombre': 'Bodega Principal - Sector A1',
                'tipo': 'bodega',
                'descripcion': 'Área principal de almacenamiento',
            },
            {
                'codigo': 'BOD-A2-001',
                'nombre': 'Bodega Principal - Sector A2',
                'tipo': 'bodega',
                'descripcion': 'Área secundaria de almacenamiento',
            },
            {
                'codigo': 'SAL-VEN-001',
                'nombre': 'Salón de Ventas - Vitrina Principal',
                'tipo': 'salon',
                'descripcion': 'Productos en exhibición para venta',
            },
            {
                'codigo': 'DEP-TEM-001',
                'nombre': 'Depósito Temporal',
                'tipo': 'deposito',
                'descripcion': 'Almacenamiento temporal de mercadería',
            },
            {
                'codigo': 'TRA-001',
                'nombre': 'En Tránsito',
                'tipo': 'transito',
                'descripcion': 'Productos en movimiento entre ubicaciones',
            }
        ]

        for ubicacion_data in ubicaciones_data:
            ubicacion, created = Ubicacion.objects.get_or_create(
                codigo=ubicacion_data['codigo'],
                defaults=ubicacion_data
            )
            if created:
                self.stdout.write(f'✅ Ubicación creada: {ubicacion.codigo}')

        # Crear configuraciones de inventario para productos existentes
        productos = Producto.objects.filter(en_venta=True)
        
        for producto in productos:
            config, created = ConfiguracionInventario.objects.get_or_create(
                producto=producto,
                defaults={
                    'stock_minimo': 10,
                    'stock_maximo': 100,
                    'punto_reorden': 20,
                    'alertas_activas': True,
                    'dias_aviso_vencimiento': 30,
                    'es_critico': False,
                    'rotacion_abc': 'C',
                }
            )
            
            if created:
                self.stdout.write(f'✅ Configuración creada para: {producto.nombre}')

        # Crear algunos lotes de inventario con datos realistas
        if productos.exists():
            proveedor = Proveedor.objects.first()
            ubicacion = Ubicacion.objects.filter(tipo='bodega').first()
            
            lotes_data = [
                {
                    'producto': productos[0],
                    'cantidad': 50,
                    'costo_unitario': Decimal('15.90'),
                },
                {
                    'producto': productos[1] if len(productos) > 1 else productos[0],
                    'cantidad': 30,
                    'costo_unitario': Decimal('25.50'),
                },
                {
                    'producto': productos[2] if len(productos) > 2 else productos[0],
                    'cantidad': 75,
                    'costo_unitario': Decimal('8.75'),
                }
            ]

            for lote_data in lotes_data:
                try:
                    lote, movimiento = InventarioService.registrar_entrada_inventario(
                        producto=lote_data['producto'],
                        cantidad=lote_data['cantidad'],
                        costo_unitario=lote_data['costo_unitario'],
                        proveedor=proveedor,
                        ubicacion=ubicacion,
                        usuario=admin_user,
                        observaciones='Inventario inicial - datos de ejemplo'
                    )
                    self.stdout.write(f'✅ Lote creado: {lote.numero_lote} para {lote.producto.nombre}')
                except Exception as e:
                    self.stdout.write(f'❌ Error creando lote para {lote_data["producto"].nombre}: {e}')

        # Configurar algunos productos como críticos
        if productos.count() >= 3:
            productos_criticos = productos[:2]
            for producto in productos_criticos:
                config = producto.configuracion_inventario
                config.es_critico = True
                config.rotacion_abc = 'A'
                config.stock_minimo = 20
                config.punto_reorden = 30
                config.save()
                self.stdout.write(f'✅ Producto configurado como crítico: {producto.nombre}')

        self.stdout.write('🎉 ¡Datos de inventario inicializados exitosamente!')
        self.stdout.write('')
        self.stdout.write('📋 RESUMEN:')
        self.stdout.write(f'   - Proveedores: {Proveedor.objects.count()}')
        self.stdout.write(f'   - Ubicaciones: {Ubicacion.objects.count()}')
        self.stdout.write(f'   - Configuraciones: {ConfiguracionInventario.objects.count()}')
        self.stdout.write(f'   - Lotes: {LoteInventario.objects.count()}')
        self.stdout.write('')
        self.stdout.write('🚀 Puedes acceder al dashboard de inventario en:')
        self.stdout.write('   http://localhost:8000/inventario/')
        self.stdout.write('')
        self.stdout.write('👤 Usuario admin: admin / admin123')
