# FerramasStore/app/domain/services/inventario_service.py
from django.db import transaction
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import datetime, timedelta

from ..models import (
    Producto, LoteInventario, MovimientoInventario, AlertaInventario,
    ConfiguracionInventario, Proveedor, Ubicacion
)

class InventarioService:
    """Servicio para gestionar operaciones de inventario"""
    
    @staticmethod
    def registrar_entrada_inventario(producto, cantidad, costo_unitario, proveedor, ubicacion, usuario, lote_numero=None, fecha_vencimiento=None, observaciones=None):
        """
        Registra una entrada de inventario (compra, devolución, etc.)
        """
        with transaction.atomic():
            # Crear o actualizar lote
            if lote_numero:
                lote, created = LoteInventario.objects.get_or_create(
                    numero_lote=lote_numero,
                    defaults={
                        'producto': producto,
                        'proveedor': proveedor,
                        'ubicacion': ubicacion,
                        'cantidad_inicial': cantidad,
                        'cantidad_actual': cantidad,
                        'costo_unitario': costo_unitario,
                        'costo_total': cantidad * costo_unitario,
                        'fecha_vencimiento': fecha_vencimiento,
                    }
                )
                
                if not created:
                    # Actualizar lote existente
                    lote.cantidad_actual += cantidad
                    lote.costo_total += (cantidad * costo_unitario)
                    lote.save()
            else:
                # Crear nuevo lote automáticamente
                lote_numero = f"LOT-{producto.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
                lote = LoteInventario.objects.create(
                    numero_lote=lote_numero,
                    producto=producto,
                    proveedor=proveedor,
                    ubicacion=ubicacion,
                    cantidad_inicial=cantidad,
                    cantidad_actual=cantidad,
                    costo_unitario=costo_unitario,
                    costo_total=cantidad * costo_unitario,
                    fecha_vencimiento=fecha_vencimiento,
                )
            
            # Actualizar stock del producto
            stock_anterior = producto.stock
            producto.stock += cantidad
            producto.save()
            
            # Registrar movimiento
            movimiento = MovimientoInventario.objects.create(
                tipo='entrada',
                motivo='compra',
                producto=producto,
                lote=lote,
                ubicacion_destino=ubicacion,
                cantidad=cantidad,
                stock_anterior=stock_anterior,
                stock_nuevo=producto.stock,
                usuario=usuario,
                observaciones=observaciones,
            )
            
            # Verificar alertas
            InventarioService.verificar_alertas_producto(producto)
            
            return lote, movimiento
    
    @staticmethod
    def registrar_salida_inventario(producto, cantidad, motivo, usuario, ubicacion_origen=None, observaciones=None, documento_referencia=None):
        """
        Registra una salida de inventario (venta, merma, etc.)
        """
        with transaction.atomic():
            # Verificar stock disponible
            if producto.stock < cantidad:
                raise ValueError(f"Stock insuficiente. Disponible: {producto.stock}, Solicitado: {cantidad}")
            
            # Obtener lotes disponibles (FIFO)
            lotes_disponibles = LoteInventario.objects.filter(
                producto=producto,
                cantidad_actual__gt=0,
                activo=True
            ).order_by('fecha_ingreso')
            
            cantidad_pendiente = cantidad
            movimientos = []
            
            for lote in lotes_disponibles:
                if cantidad_pendiente <= 0:
                    break
                
                cantidad_a_tomar = min(cantidad_pendiente, lote.cantidad_disponible)
                
                if cantidad_a_tomar > 0:
                    # Actualizar lote
                    stock_anterior = producto.stock
                    lote.cantidad_actual -= cantidad_a_tomar
                    lote.save()
                    
                    # Actualizar stock del producto
                    producto.stock -= cantidad_a_tomar
                    producto.save()
                    
                    # Registrar movimiento
                    movimiento = MovimientoInventario.objects.create(
                        tipo='salida',
                        motivo=motivo,
                        producto=producto,
                        lote=lote,
                        ubicacion_origen=ubicacion_origen,
                        cantidad=cantidad_a_tomar,
                        stock_anterior=stock_anterior,
                        stock_nuevo=producto.stock,
                        usuario=usuario,
                        observaciones=observaciones,
                        documento_referencia=documento_referencia,
                    )
                    
                    movimientos.append(movimiento)
                    cantidad_pendiente -= cantidad_a_tomar
            
            if cantidad_pendiente > 0:
                raise ValueError(f"No se pudo procesar toda la cantidad. Faltante: {cantidad_pendiente}")
            
            # Verificar alertas
            InventarioService.verificar_alertas_producto(producto)
            
            return movimientos
    
    @staticmethod
    def reservar_stock(producto, cantidad, usuario, observaciones=None):
        """
        Reserva stock para una venta
        """
        with transaction.atomic():
            # Verificar stock disponible
            stock_disponible = InventarioService.calcular_stock_disponible(producto)
            if stock_disponible < cantidad:
                raise ValueError(f"Stock disponible insuficiente. Disponible: {stock_disponible}, Solicitado: {cantidad}")
            
            # Obtener lotes disponibles (FIFO)
            lotes_disponibles = LoteInventario.objects.filter(
                producto=producto,
                cantidad_actual__gt=0,
                activo=True
            ).order_by('fecha_ingreso')
            
            cantidad_pendiente = cantidad
            reservas = []
            
            for lote in lotes_disponibles:
                if cantidad_pendiente <= 0:
                    break
                
                cantidad_a_reservar = min(cantidad_pendiente, lote.cantidad_disponible)
                
                if cantidad_a_reservar > 0:
                    # Actualizar reserva del lote
                    lote.reservado += cantidad_a_reservar
                    lote.save()
                    
                    # Registrar movimiento
                    movimiento = MovimientoInventario.objects.create(
                        tipo='reserva',
                        motivo='reserva_venta',
                        producto=producto,
                        lote=lote,
                        cantidad=cantidad_a_reservar,
                        stock_anterior=producto.stock,
                        stock_nuevo=producto.stock,
                        usuario=usuario,
                        observaciones=observaciones,
                    )
                    
                    reservas.append(movimiento)
                    cantidad_pendiente -= cantidad_a_reservar
            
            return reservas
    
    @staticmethod
    def liberar_reserva(producto, cantidad, usuario, observaciones=None):
        """
        Libera una reserva de stock
        """
        with transaction.atomic():
            # Obtener lotes con reservas (FIFO)
            lotes_con_reservas = LoteInventario.objects.filter(
                producto=producto,
                reservado__gt=0,
                activo=True
            ).order_by('fecha_ingreso')
            
            cantidad_pendiente = cantidad
            liberaciones = []
            
            for lote in lotes_con_reservas:
                if cantidad_pendiente <= 0:
                    break
                
                cantidad_a_liberar = min(cantidad_pendiente, lote.reservado)
                
                if cantidad_a_liberar > 0:
                    # Actualizar reserva del lote
                    lote.reservado -= cantidad_a_liberar
                    lote.save()
                    
                    # Registrar movimiento
                    movimiento = MovimientoInventario.objects.create(
                        tipo='liberacion',
                        motivo='liberacion_reserva',
                        producto=producto,
                        lote=lote,
                        cantidad=cantidad_a_liberar,
                        stock_anterior=producto.stock,
                        stock_nuevo=producto.stock,
                        usuario=usuario,
                        observaciones=observaciones,
                    )
                    
                    liberaciones.append(movimiento)
                    cantidad_pendiente -= cantidad_a_liberar
            
            return liberaciones
    
    @staticmethod
    def calcular_stock_disponible(producto):
        """
        Calcula el stock disponible (actual - reservado)
        """
        lotes = LoteInventario.objects.filter(producto=producto, activo=True)
        total_disponible = sum(lote.cantidad_disponible for lote in lotes)
        return total_disponible
    
    @staticmethod
    def verificar_alertas_producto(producto):
        """
        Verifica y crea alertas para un producto
        """
        try:
            config = producto.configuracion_inventario
        except ConfiguracionInventario.DoesNotExist:
            # Crear configuración por defecto
            config = ConfiguracionInventario.objects.create(producto=producto)
        
        if not config.alertas_activas:
            return
        
        stock_actual = producto.stock
        stock_disponible = InventarioService.calcular_stock_disponible(producto)
        
        # Verificar stock bajo
        if stock_disponible <= config.stock_minimo:
            tipo_alerta = 'stock_critico' if stock_disponible <= (config.stock_minimo * 0.5) else 'stock_bajo'
            
            # Verificar si ya existe una alerta activa
            alerta_existente = AlertaInventario.objects.filter(
                producto=producto,
                tipo=tipo_alerta,
                estado='pendiente'
            ).first()
            
            if not alerta_existente:
                AlertaInventario.objects.create(
                    producto=producto,
                    tipo=tipo_alerta,
                    stock_actual=stock_actual,
                    stock_minimo=config.stock_minimo,
                    mensaje=f"Stock {tipo_alerta.replace('_', ' ')} para {producto.nombre}. Stock actual: {stock_disponible}, Mínimo: {config.stock_minimo}"
                )
        
        # Verificar sobre stock
        if stock_actual > config.stock_maximo:
            alerta_existente = AlertaInventario.objects.filter(
                producto=producto,
                tipo='sobre_stock',
                estado='pendiente'
            ).first()
            
            if not alerta_existente:
                AlertaInventario.objects.create(
                    producto=producto,
                    tipo='sobre_stock',
                    stock_actual=stock_actual,
                    stock_maximo=config.stock_maximo,
                    mensaje=f"Sobre stock detectado para {producto.nombre}. Stock actual: {stock_actual}, Máximo: {config.stock_maximo}"
                )
        
        # Verificar productos próximos a vencer
        fecha_limite = timezone.now().date() + timedelta(days=config.dias_aviso_vencimiento)
        
        lotes_por_vencer = LoteInventario.objects.filter(
            producto=producto,
            fecha_vencimiento__lte=fecha_limite,
            fecha_vencimiento__gte=timezone.now().date(),
            cantidad_actual__gt=0
        )
        
        for lote in lotes_por_vencer:
            alerta_existente = AlertaInventario.objects.filter(
                producto=producto,
                tipo='producto_por_vencer',
                estado='pendiente'
            ).first()
            
            if not alerta_existente:
                AlertaInventario.objects.create(
                    producto=producto,
                    tipo='producto_por_vencer',
                    stock_actual=stock_actual,
                    mensaje=f"Producto {producto.nombre} próximo a vencer. Lote: {lote.numero_lote}, Vencimiento: {lote.fecha_vencimiento}"
                )
    
    @staticmethod
    def generar_reporte_inventario(fecha_inicio=None, fecha_fin=None):
        """
        Genera reporte de inventario
        """
        if not fecha_inicio:
            fecha_inicio = timezone.now().date() - timedelta(days=30)
        if not fecha_fin:
            fecha_fin = timezone.now().date()
        
        productos = Producto.objects.filter(en_venta=True)
        reporte = []
        
        for producto in productos:
            stock_disponible = InventarioService.calcular_stock_disponible(producto)
            
            # Calcular valor del inventario
            lotes = LoteInventario.objects.filter(producto=producto, activo=True)
            valor_inventario = sum(lote.valor_inventario for lote in lotes)
            
            # Movimientos en el período
            movimientos = MovimientoInventario.objects.filter(
                producto=producto,
                fecha__date__gte=fecha_inicio,
                fecha__date__lte=fecha_fin
            )
            
            entradas = movimientos.filter(tipo='entrada').aggregate(total=models.Sum('cantidad'))['total'] or 0
            salidas = movimientos.filter(tipo='salida').aggregate(total=models.Sum('cantidad'))['total'] or 0
            
            try:
                config = producto.configuracion_inventario
                stock_minimo = config.stock_minimo
                stock_maximo = config.stock_maximo
            except ConfiguracionInventario.DoesNotExist:
                stock_minimo = 0
                stock_maximo = 0
            
            reporte.append({
                'producto': producto,
                'stock_actual': producto.stock,
                'stock_disponible': stock_disponible,
                'stock_reservado': producto.stock - stock_disponible,
                'stock_minimo': stock_minimo,
                'stock_maximo': stock_maximo,
                'valor_inventario': valor_inventario,
                'entradas_periodo': entradas,
                'salidas_periodo': salidas,
                'rotacion': salidas / max(producto.stock, 1) if producto.stock > 0 else 0,
                'estado': 'Crítico' if stock_disponible <= (stock_minimo * 0.5) else 'Bajo' if stock_disponible <= stock_minimo else 'Normal'
            })
        
        return reporte
