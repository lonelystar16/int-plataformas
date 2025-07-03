/**
 * Voucher Management - Ferramas Store
 * Maneja la lógica del voucher de pago
 */

class VoucherManager {
    constructor() {
        this.init();
    }

    init() {
        // Verificar si hay datos del voucher desde Django
        if (window.voucherData) {
            this.cargarVoucher(window.voucherData);
        } else {
            // Fallback: intentar cargar desde sessionStorage
            this.cargarDesdeSessionStorage();
        }
        
        // Configurar event listeners para los botones
        this.configurarEventListeners();
    }

    /**
     * Configura los event listeners para los botones del voucher
     */
    configurarEventListeners() {
        // Botón de imprimir
        const btnImprimir = document.getElementById('btn-imprimir');
        if (btnImprimir) {
            btnImprimir.addEventListener('click', this.imprimirVoucher.bind(this));
        }

        // Botón de volver al inicio
        const btnVolver = document.getElementById('btn-volver');
        if (btnVolver) {
            btnVolver.addEventListener('click', this.volverAlInicio.bind(this));
        }
    }

    /**
     * Carga los datos del voucher en la interfaz
     * @param {Object} datosVoucher - Datos del voucher
     */
    cargarVoucher(datosVoucher) {
        try {
            // Información básica
            this.setElementText('voucher-number', `N° ${datosVoucher.numero_voucher}`);
            this.setElementText('comprador-nombre', datosVoucher.comprador);
            this.setElementText('fecha-pago', datosVoucher.fecha);
            this.setElementText('metodo-pago', this.formatearMetodoPago(datosVoucher.metodo_pago));
            
            // Mostrar tipo de cliente
            const tipoCliente = datosVoucher.es_usuario_registrado 
                ? 'Cliente registrado (10% descuento aplicado)' 
                : 'Cliente invitado';
            this.setElementText('tipo-cliente', tipoCliente);
            
            // Cargar totales
            this.cargarTotales(datosVoucher);
            
            // Cargar productos
            this.cargarProductos(datosVoucher.productos);
            
        } catch (error) {
            console.error('Error al cargar voucher:', error);
            this.mostrarError('Error al cargar los datos del voucher');
        }
    }

    /**
     * Carga los totales del voucher
     * @param {Object} datosVoucher - Datos del voucher
     */
    cargarTotales(datosVoucher) {
        // Totales principales
        this.setElementText('total-pago', this.formatearMoneda(datosVoucher.total));
        this.setElementText('subtotal-original', this.formatearMoneda(datosVoucher.subtotal));
        this.setElementText('subtotal-neto', this.formatearMoneda(datosVoucher.subtotal_con_descuento));
        this.setElementText('iva-monto', this.formatearMoneda(datosVoucher.iva));
        this.setElementText('total-final', this.formatearMoneda(datosVoucher.total));
        
        // Mostrar descuento si aplica
        if (datosVoucher.descuento > 0) {
            const descuentoRow = document.getElementById('descuento-row');
            if (descuentoRow) {
                descuentoRow.style.display = 'flex';
                this.setElementText('descuento-monto', `-${this.formatearMoneda(datosVoucher.descuento)}`);
            }
        }
    }

    /**
     * Carga la tabla de productos
     * @param {Array} productos - Lista de productos
     */
    cargarProductos(productos) {
        const productosDetalle = document.getElementById('productos-detalle');
        if (!productosDetalle) return;

        productosDetalle.innerHTML = '';
        
        productos.forEach(producto => {
            const subtotalProducto = producto.precio * producto.cantidad;
            const fila = this.crearFilaProducto(producto, subtotalProducto);
            productosDetalle.innerHTML += fila;
        });
    }

    /**
     * Crea una fila de producto para la tabla
     * @param {Object} producto - Datos del producto
     * @param {number} subtotal - Subtotal del producto
     * @returns {string} HTML de la fila
     */
    crearFilaProducto(producto, subtotal) {
        return `
            <tr class="border-t">
                <td class="px-4 py-2 text-sm">${this.escapeHtml(producto.nombre)}</td>
                <td class="px-4 py-2 text-center text-sm">${producto.cantidad}</td>
                <td class="px-4 py-2 text-right text-sm">${this.formatearMoneda(producto.precio)}</td>
                <td class="px-4 py-2 text-right text-sm">${this.formatearMoneda(subtotal)}</td>
            </tr>
        `;
    }

    /**
     * Intenta cargar datos desde sessionStorage como fallback
     */
    cargarDesdeSessionStorage() {
        const sessionVoucherData = sessionStorage.getItem('voucherData');
        if (sessionVoucherData) {
            try {
                const datos = JSON.parse(sessionVoucherData);
                this.cargarVoucher(datos);
                sessionStorage.removeItem('voucherData'); // Limpiar después de usar
            } catch (error) {
                console.error('Error al parsear datos de sessionStorage:', error);
                this.mostrarError('Error al cargar datos del voucher');
            }
        } else {
            this.mostrarAccesoDenegado();
        }
    }

    /**
     * Muestra mensaje de acceso denegado
     */
    mostrarAccesoDenegado() {
        const container = document.querySelector('.max-w-2xl');
        if (container) {
            container.innerHTML = `
                <div class="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
                    <div class="text-red-600 mb-4">
                        <svg class="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4H21a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 002 2v10a2 2 0 002 2z" />
                        </svg>
                    </div>
                    <h2 class="text-xl font-bold text-red-800 mb-2">Acceso Denegado</h2>
                    <p class="text-red-700 mb-4">No tienes permiso para acceder a esta página.</p>
                    <a href="/" class="bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded">
                        Volver al Inicio
                    </a>
                </div>
            `;
        }
    }

    /**
     * Muestra mensaje de error genérico
     * @param {string} mensaje - Mensaje de error
     */
    mostrarError(mensaje) {
        const container = document.querySelector('.max-w-2xl');
        if (container) {
            container.innerHTML = `
                <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-8 text-center">
                    <h2 class="text-xl font-bold text-yellow-800 mb-2">Error</h2>
                    <p class="text-yellow-700 mb-4">${mensaje}</p>
                    <a href="/" class="bg-yellow-600 hover:bg-yellow-700 text-white font-semibold py-2 px-4 rounded">
                        Volver al Inicio
                    </a>
                </div>
            `;
        }
    }

    // Métodos utilitarios

    /**
     * Establece el texto de un elemento por ID
     * @param {string} elementId - ID del elemento
     * @param {string} text - Texto a establecer
     */
    setElementText(elementId, text) {
        FerramasUtils.setElementText(elementId, text);
    }

    /**
     * Formatea un método de pago
     * @param {string} metodo - Método de pago
     * @returns {string} Método formateado
     */
    formatearMetodoPago(metodo) {
        const metodos = {
            'tarjeta': 'Tarjeta de Crédito/Débito',
            'transferencia': 'Transferencia Bancaria'
        };
        return metodos[metodo] || metodo;
    }

    /**
     * Formatea un número como moneda chilena
     * @param {number} valor - Valor a formatear
     * @returns {string} Valor formateado
     */
    formatearMoneda(valor) {
        return FerramasUtils.formatearMoneda(valor);
    }

    /**
     * Escapa HTML para prevenir XSS
     * @param {string} text - Texto a escapar
     * @returns {string} Texto escapado
     */
    escapeHtml(text) {
        return FerramasUtils.escapeHtml(text);
    }

    /**
     * Imprime el voucher
     */
    imprimirVoucher() {
        window.print();
    }

    /**
     * Navega al inicio de la aplicación
     */
    volverAlInicio() {
        window.location.href = '/';
    }
}

// Funciones globales para compatibilidad (deprecated - usar VoucherManager)
window.VoucherManager = VoucherManager;

// Auto-inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    window.voucherManager = new VoucherManager();
});
