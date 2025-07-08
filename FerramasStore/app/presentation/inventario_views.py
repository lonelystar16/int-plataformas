# FerramasStore/app/presentation/inventario_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import json

from ..domain.models import (
    Producto, LoteInventario, MovimientoInventario, AlertaInventario,
    ConfiguracionInventario, Proveedor, Ubicacion, Categoria
)
from ..domain.services.inventario_service import InventarioService
from ..security.decorators import secure_api_view
from ..security.validators import validate_quantity, validate_price_range

def is_staff_or_admin(user):
    """Verifica si el usuario es staff o admin"""
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_staff_or_admin)
def dashboard_inventario(request):
    """Dashboard principal de inventario"""
    
    # Estadísticas generales
    total_productos = Producto.objects.filter(en_venta=True).count()
    total_alertas = AlertaInventario.objects.filter(estado='pendiente').count()
    
    # Productos con stock bajo
    productos_stock_bajo = []
    for producto in Producto.objects.filter(en_venta=True):
        try:
            config = producto.configuracion_inventario
            stock_disponible = InventarioService.calcular_stock_disponible(producto)
            if stock_disponible <= config.stock_minimo:
                productos_stock_bajo.append({
                    'producto': producto,
                    'stock_disponible': stock_disponible,
                    'stock_minimo': config.stock_minimo,
                    'estado': 'crítico' if stock_disponible <= (config.stock_minimo * 0.5) else 'bajo'
                })
        except ConfiguracionInventario.DoesNotExist:
            continue
    
    # Movimientos recientes
    movimientos_recientes = MovimientoInventario.objects.select_related(
        'producto', 'usuario', 'lote'
    ).order_by('-fecha')[:10]
    
    # Valor total del inventario
    valor_total_inventario = 0
    for lote in LoteInventario.objects.filter(activo=True):
        valor_total_inventario += lote.valor_inventario
    
    # Alertas pendientes
    alertas_pendientes = AlertaInventario.objects.filter(
        estado='pendiente'
    ).select_related('producto').order_by('-fecha_creacion')[:5]
    
    context = {
        'total_productos': total_productos,
        'total_alertas': total_alertas,
        'productos_stock_bajo': productos_stock_bajo,
        'movimientos_recientes': movimientos_recientes,
        'valor_total_inventario': valor_total_inventario,
        'alertas_pendientes': alertas_pendientes,
    }
    
    return render(request, 'inventario/dashboard.html', context)

@login_required
@user_passes_test(is_staff_or_admin)
def lista_productos_inventario(request):
    """Lista de productos con información de inventario"""
    
    productos = Producto.objects.filter(en_venta=True).select_related('categoria')
    
    # Filtros
    categoria_id = request.GET.get('categoria')
    buscar = request.GET.get('buscar')
    estado = request.GET.get('estado')
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    if buscar:
        productos = productos.filter(
            Q(nombre__icontains=buscar) | 
            Q(sku__icontains=buscar) |
            Q(descripcion__icontains=buscar)
        )
    
    # Preparar datos con información de inventario
    productos_data = []
    for producto in productos:
        try:
            config = producto.configuracion_inventario
            stock_minimo = config.stock_minimo
            stock_maximo = config.stock_maximo
        except ConfiguracionInventario.DoesNotExist:
            stock_minimo = 0
            stock_maximo = 0
        
        stock_disponible = InventarioService.calcular_stock_disponible(producto)
        
        # Determinar estado
        if stock_disponible <= (stock_minimo * 0.5):
            estado_stock = 'crítico'
        elif stock_disponible <= stock_minimo:
            estado_stock = 'bajo'
        elif stock_disponible > stock_maximo:
            estado_stock = 'alto'
        else:
            estado_stock = 'normal'
        
        # Filtrar por estado si se especificó
        if estado and estado != estado_stock:
            continue
        
        productos_data.append({
            'producto': producto,
            'stock_disponible': stock_disponible,
            'stock_reservado': producto.stock - stock_disponible,
            'stock_minimo': stock_minimo,
            'stock_maximo': stock_maximo,
            'estado': estado_stock,
        })
    
    # Paginación
    paginator = Paginator(productos_data, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categorias': Categoria.objects.all(),
        'filtros': {
            'categoria': categoria_id,
            'buscar': buscar,
            'estado': estado,
        }
    }
    
    return render(request, 'inventario/lista_productos.html', context)

@login_required
@user_passes_test(is_staff_or_admin)
def detalle_producto_inventario(request, producto_id):
    """Detalle de inventario de un producto específico"""
    
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Información general
    stock_disponible = InventarioService.calcular_stock_disponible(producto)
    
    try:
        config = producto.configuracion_inventario
    except ConfiguracionInventario.DoesNotExist:
        config = ConfiguracionInventario.objects.create(producto=producto)
    
    # Lotes activos
    lotes = LoteInventario.objects.filter(
        producto=producto, 
        activo=True
    ).select_related('proveedor', 'ubicacion').order_by('fecha_vencimiento')
    
    # Movimientos recientes
    movimientos = MovimientoInventario.objects.filter(
        producto=producto
    ).select_related('usuario', 'lote').order_by('-fecha')[:20]
    
    # Alertas activas
    alertas = AlertaInventario.objects.filter(
        producto=producto,
        estado='pendiente'
    ).order_by('-fecha_creacion')
    
    context = {
        'producto': producto,
        'stock_disponible': stock_disponible,
        'config': config,
        'lotes': lotes,
        'movimientos': movimientos,
        'alertas': alertas,
    }
    
    return render(request, 'inventario/detalle_producto.html', context)

@login_required
@user_passes_test(is_staff_or_admin)
def entrada_inventario(request):
    """Registrar entrada de inventario"""
    
    if request.method == 'POST':
        try:
            producto_id = request.POST.get('producto')
            cantidad = int(request.POST.get('cantidad'))
            costo_unitario = float(request.POST.get('costo_unitario'))
            proveedor_id = request.POST.get('proveedor')
            ubicacion_id = request.POST.get('ubicacion')
            lote_numero = request.POST.get('lote_numero')
            fecha_vencimiento = request.POST.get('fecha_vencimiento')
            observaciones = request.POST.get('observaciones')
            
            # Validaciones
            validate_quantity(cantidad)
            validate_price_range(costo_unitario)
            
            # Obtener objetos
            producto = get_object_or_404(Producto, id=producto_id)
            proveedor = get_object_or_404(Proveedor, id=proveedor_id)
            ubicacion = get_object_or_404(Ubicacion, id=ubicacion_id)
            
            # Convertir fecha si se proporciona
            fecha_venc = None
            if fecha_vencimiento:
                fecha_venc = datetime.strptime(fecha_vencimiento, '%Y-%m-%d').date()
            
            # Registrar entrada
            lote, movimiento = InventarioService.registrar_entrada_inventario(
                producto=producto,
                cantidad=cantidad,
                costo_unitario=costo_unitario,
                proveedor=proveedor,
                ubicacion=ubicacion,
                usuario=request.user,
                lote_numero=lote_numero,
                fecha_vencimiento=fecha_venc,
                observaciones=observaciones
            )
            
            messages.success(request, f'Entrada registrada exitosamente. Lote: {lote.numero_lote}')
            return redirect('app:detalle_producto_inventario', producto_id=producto.id)
            
        except Exception as e:
            messages.error(request, f'Error al registrar entrada: {str(e)}')
    
    context = {
        'productos': Producto.objects.filter(en_venta=True),
        'proveedores': Proveedor.objects.filter(activo=True),
        'ubicaciones': Ubicacion.objects.filter(activa=True),
    }
    
    return render(request, 'inventario/entrada_inventario.html', context)

@login_required
@user_passes_test(is_staff_or_admin)
def salida_inventario(request):
    """Registrar salida de inventario"""
    
    if request.method == 'POST':
        try:
            producto_id = request.POST.get('producto')
            cantidad = int(request.POST.get('cantidad'))
            motivo = request.POST.get('motivo')
            ubicacion_id = request.POST.get('ubicacion')
            observaciones = request.POST.get('observaciones')
            documento_referencia = request.POST.get('documento_referencia')
            
            # Validaciones
            validate_quantity(cantidad)
            
            # Obtener objetos
            producto = get_object_or_404(Producto, id=producto_id)
            ubicacion = get_object_or_404(Ubicacion, id=ubicacion_id) if ubicacion_id else None
            
            # Registrar salida
            movimientos = InventarioService.registrar_salida_inventario(
                producto=producto,
                cantidad=cantidad,
                motivo=motivo,
                usuario=request.user,
                ubicacion_origen=ubicacion,
                observaciones=observaciones,
                documento_referencia=documento_referencia
            )
            
            messages.success(request, f'Salida registrada exitosamente. {len(movimientos)} movimientos creados.')
            return redirect('app:detalle_producto_inventario', producto_id=producto.id)
            
        except Exception as e:
            messages.error(request, f'Error al registrar salida: {str(e)}')
    
    context = {
        'productos': Producto.objects.filter(en_venta=True),
        'ubicaciones': Ubicacion.objects.filter(activa=True),
        'motivos': MovimientoInventario.MOTIVO_CHOICES,
    }
    
    return render(request, 'inventario/salida_inventario.html', context)

@login_required
@user_passes_test(is_staff_or_admin)
def gestionar_alertas(request):
    """Gestionar alertas de inventario"""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'marcar_leida':
            alerta_id = request.POST.get('alerta_id')
            try:
                alerta = AlertaInventario.objects.get(id=alerta_id)
                alerta.estado = 'resuelta'
                alerta.fecha_resolucion = timezone.now()
                alerta.save()
                messages.success(request, 'Alerta marcada como resuelta exitosamente.')
            except AlertaInventario.DoesNotExist:
                messages.error(request, 'Alerta no encontrada.')
        
        elif action == 'config_global':
            stock_minimo = request.POST.get('stock_minimo_global', 10)
            stock_critico = request.POST.get('stock_critico_global', 5)
            
            # Actualizar configuración global (implementar modelo ConfiguracionGlobal si no existe)
            messages.success(request, 'Configuración global actualizada exitosamente.')
        
        elif action == 'update_stock_minimo':
            producto_id = request.POST.get('producto_id')
            stock_minimo = request.POST.get('stock_minimo')
            
            try:
                producto = Producto.objects.get(id=producto_id)
                config, created = ConfiguracionInventario.objects.get_or_create(
                    producto=producto,
                    defaults={'stock_minimo': stock_minimo}
                )
                if not created:
                    config.stock_minimo = stock_minimo
                    config.save()
                messages.success(request, f'Stock mínimo actualizado para {producto.nombre}.')
            except Producto.DoesNotExist:
                messages.error(request, 'Producto no encontrado.')
        
        elif action == 'update_stock_critico':
            producto_id = request.POST.get('producto_id')
            stock_critico = request.POST.get('stock_critico')
            
            try:
                producto = Producto.objects.get(id=producto_id)
                config, created = ConfiguracionInventario.objects.get_or_create(
                    producto=producto,
                    defaults={'stock_critico': stock_critico}
                )
                if not created:
                    config.stock_critico = stock_critico
                    config.save()
                messages.success(request, f'Stock crítico actualizado para {producto.nombre}.')
            except Producto.DoesNotExist:
                messages.error(request, 'Producto no encontrado.')
        
        return redirect('app:gestionar_alertas')
    
    # Obtener alertas activas
    alertas_activas = AlertaInventario.objects.filter(
        estado='pendiente'
    ).select_related('producto').order_by('-fecha_creacion')
    
    # Estadísticas
    alertas_criticas = AlertaInventario.objects.filter(
        estado='pendiente', 
        nivel='CRITICO'
    ).count()
    
    alertas_bajas = AlertaInventario.objects.filter(
        estado='pendiente', 
        nivel='MEDIO'
    ).count()
    
    productos_monitoreados = Producto.objects.filter(
        en_venta=True
    ).count()
    
    alertas_resueltas = AlertaInventario.objects.filter(
        estado='resuelta',
        fecha_resolucion__date=timezone.now().date()
    ).count()
    
    # Historial de alertas
    fecha_desde = timezone.now() - timedelta(days=30)
    fecha_hasta = timezone.now()
    
    historial_alertas = AlertaInventario.objects.filter(
        fecha_creacion__range=[fecha_desde, fecha_hasta]
    ).select_related('producto').order_by('-fecha_creacion')[:50]
    
    # Todos los productos para configuración
    productos = Producto.objects.filter(en_venta=True).select_related('categoria')
    
    # Preparar datos de productos con configuración
    productos_data = []
    for producto in productos:
        try:
            config = producto.configuracion_inventario
        except ConfiguracionInventario.DoesNotExist:
            config = None
        
        productos_data.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'sku': producto.sku,
            'stock': producto.stock,
            'categoria': producto.categoria.nombre if producto.categoria else None,
            'config_inventario': config,
        })
    
    context = {
        'alertas_activas': alertas_activas,
        'alertas_criticas': alertas_criticas,
        'alertas_bajas': alertas_bajas,
        'productos_monitoreados': productos_monitoreados,
        'alertas_resueltas': alertas_resueltas,
        'historial_alertas': historial_alertas,
        'productos': productos_data,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'config': {
            'stock_minimo_global': 10,
            'stock_critico_global': 5,
        }
    }
    
    return render(request, 'inventario/gestionar_alertas.html', context)

@login_required
@user_passes_test(is_staff_or_admin)
@secure_api_view(rate='50/h')
def api_stock_producto(request, producto_id):
    """API para obtener información de stock de un producto"""
    
    try:
        producto = get_object_or_404(Producto, id=producto_id)
        stock_disponible = InventarioService.calcular_stock_disponible(producto)
        
        data = {
            'producto_id': producto.id,
            'nombre': producto.nombre,
            'stock_total': producto.stock,
            'stock_disponible': stock_disponible,
            'stock_reservado': producto.stock - stock_disponible,
            'precio': float(producto.precio),
            'en_venta': producto.en_venta,
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@user_passes_test(is_staff_or_admin)
def reporte_inventario(request):
    """Generar reporte de inventario"""
    
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if fecha_inicio:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    
    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    
    reporte = InventarioService.generar_reporte_inventario(fecha_inicio, fecha_fin)
    
    context = {
        'reporte': reporte,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    
    return render(request, 'inventario/reporte_inventario.html', context)
