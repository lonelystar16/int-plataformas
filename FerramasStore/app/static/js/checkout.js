/**
 * Checkout Management - Ferramas Store
 * Maneja la lógica del carrito de compras y procesamiento de pagos
 */

class CheckoutManager {
    constructor() {
        this.cart = {};
        this.total = 0;
        this.discountPercentage = window.discountPercentage || 0;
        this.isAuthenticated = window.isAuthenticated || false;
        this.init();
    }

    init() {
        this.loadCart();
        this.renderCart();
        this.setupEventListeners();
        this.updateTotal();
    }

    /**
     * Carga el carrito desde localStorage
     */
    loadCart() {
        this.cart = JSON.parse(localStorage.getItem('cart')) || {};
    }

    /**
     * Renderiza los elementos del carrito
     */
    renderCart() {
        const cartItemsDiv = document.getElementById('cart-items');
        if (!cartItemsDiv) return;

        const cartValues = Object.values(this.cart);
        
        if (cartValues.length === 0) {
            cartItemsDiv.innerHTML = '<p class="text-gray-500">El carrito está vacío.</p>';
            return;
        }

        let cartHTML = '';
        Object.entries(this.cart).forEach(([id, item]) => {
            cartHTML += this.createCartItemHTML(item);
            this.total += item.precio * item.cantidad;
        });

        cartItemsDiv.innerHTML = cartHTML;
    }

    /**
     * Crea el HTML para un elemento del carrito
     * @param {Object} item - Elemento del carrito
     * @returns {string} HTML del elemento
     */
    createCartItemHTML(item) {
        return `
            <div class="flex items-center gap-4 border-b pb-4">
                <img src="https://via.placeholder.com/100" alt="Producto" class="w-24 h-24 object-cover rounded" />
                <div>
                    <p class="font-semibold">Precio: ${this.formatearMoneda(item.precio)}</p>
                    <p>Descripcion: ${this.escapeHtml(item.nombre)}</p>
                    <p>Cantidad: ${item.cantidad}</p>
                </div>
            </div>
        `;
    }

    /**
     * Actualiza el total mostrado
     */
    updateTotal() {
        let finalTotal = this.total;

        // Aplicar descuento si existe
        if (this.discountPercentage > 0) {
            finalTotal = this.total * (1 - this.discountPercentage / 100);
            document.getElementById('total').innerHTML = `
                <span class="text-base line-through mr-2">${this.formatearMoneda(this.total)}</span>
                <span class="text-2xl font-bold">${this.formatearMoneda(finalTotal)}</span>
            `;
        } else {
            document.getElementById('total').innerHTML = `<strong>${this.formatearMoneda(finalTotal)}</strong>`;
        }
    }

    /**
     * Configura los event listeners
     */
    setupEventListeners() {
        // Botón de volver
        const btnVolver = document.getElementById('btn-volver');
        if (btnVolver) {
            btnVolver.addEventListener('click', () => window.history.back());
        }

        // Botón de continuar pago (para invitados)
        const btnContinuarPago = document.getElementById('btn-continuar-pago');
        if (btnContinuarPago) {
            btnContinuarPago.addEventListener('click', () => this.validarYProcesarPago());
        }

        // Botón de transferencia (toggle)
        const transferButton = document.getElementById('transfer-button');
        if (transferButton) {
            transferButton.addEventListener('click', () => this.toggleTransferDetails());
        }

        // Botón de pago con tarjeta
        const pagarTarjetaButton = document.getElementById('pagar-tarjeta');
        if (pagarTarjetaButton) {
            pagarTarjetaButton.addEventListener('click', () => this.procesarPago('tarjeta'));
        }

        // Botón de confirmar transferencia
        const confirmarTransferenciaButton = document.getElementById('confirmar-transferencia');
        if (confirmarTransferenciaButton) {
            confirmarTransferenciaButton.addEventListener('click', () => this.procesarPago('transferencia'));
        }
    }

    /**
     * Toggle de los detalles de transferencia
     */
    toggleTransferDetails() {
        const transferDetails = document.getElementById('transfer-details');
        if (transferDetails) {
            transferDetails.classList.toggle('hidden');
        }
    }

    /**
     * Valida y procesa el pago (para clientes invitados)
     */
    validarYProcesarPago() {
        if (!this.isAuthenticated) {
            const guestName = document.getElementById('guest-name');
            if (!guestName || !guestName.value.trim()) {
                alert('Por favor, ingresa tu nombre completo');
                if (guestName) guestName.focus();
                return;
            }
        }
        
        // Mostrar los botones de pago
        const paymentButtons = document.querySelector('.flex.w-full.gap-2.mb-4');
        if (paymentButtons) {
            paymentButtons.style.display = 'flex';
        }
    }

    /**
     * Procesa el pago
     * @param {string} metodoPago - Método de pago ('tarjeta' o 'transferencia')
     */
    async procesarPago(metodoPago) {
        if (Object.keys(this.cart).length === 0) {
            alert('El carrito está vacío');
            return;
        }

        // Preparar datos del carrito
        const productos = Object.values(this.cart).map(item => ({
            nombre: item.nombre,
            precio: item.precio,
            cantidad: item.cantidad
        }));

        const pagoData = {
            productos: productos,
            metodo_pago: metodoPago
        };

        // Si no está autenticado, agregar datos del cliente invitado
        if (!this.isAuthenticated) {
            const guestName = document.getElementById('guest-name');
            const guestEmail = document.getElementById('guest-email');

            if (!guestName || !guestName.value.trim()) {
                alert('Por favor, ingresa tu nombre completo');
                if (guestName) guestName.focus();
                return;
            }

            pagoData.datos_cliente = {
                nombre: guestName.value.trim(),
                email: guestEmail ? guestEmail.value.trim() : ''
            };
        }

        // Mostrar loading
        const button = metodoPago === 'tarjeta' 
            ? document.getElementById('pagar-tarjeta')
            : document.getElementById('confirmar-transferencia');
        
        this.showLoading(button);

        try {
            const response = await fetch('/pagos/procesar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify(pagoData)
            });

            const data = await response.json();

            if (data.success) {
                // Limpiar carrito
                localStorage.removeItem('cart');
                
                // Guardar datos del voucher como fallback
                sessionStorage.setItem('voucherData', JSON.stringify(data));
                
                // Redirigir al voucher (con token para mayor seguridad)
                window.location.href = `/pagos/voucher/${data.voucher_id}/`;
            } else {
                alert('Error al procesar el pago: ' + data.error);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al procesar el pago. Intente nuevamente.');
        } finally {
            this.hideLoading(button);
        }
    }

    /**
     * Muestra estado de carga en un botón
     * @param {HTMLElement} button - Botón a modificar
     */
    showLoading(button) {
        if (button) {
            button.dataset.originalText = button.textContent;
            button.textContent = 'Procesando...';
            button.disabled = true;
        }
    }

    /**
     * Oculta estado de carga de un botón
     * @param {HTMLElement} button - Botón a restaurar
     */
    hideLoading(button) {
        if (button) {
            button.textContent = button.dataset.originalText || button.textContent;
            button.disabled = false;
        }
    }

    /**
     * Obtiene el token CSRF
     * @param {string} name - Nombre de la cookie
     * @returns {string|null} Valor de la cookie
     */
    getCookie(name) {
        return FerramasUtils.getCookie(name);
    }

    // Métodos utilitarios

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
}

// Funciones globales para compatibilidad
window.CheckoutManager = CheckoutManager;

// Función global para validar y procesar pago (compatibilidad con template)
function validarYProcesarPago() {
    if (window.checkoutManager) {
        window.checkoutManager.validarYProcesarPago();
    }
}

// Auto-inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    window.checkoutManager = new CheckoutManager();
});
