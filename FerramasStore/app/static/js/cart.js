/**
 * Shopping Cart Component
 * Componente de carrito de compras reutilizable
 * Versión: 1.0.0
 */

// Verificación inmediata de que el script se está ejecutando
window.cartScriptLoaded = true;

class ShoppingCart {
  constructor(options = {}) {
    // Configuración por defecto
    this.config = {
      storageKey: options.storageKey || "cart",
      currency: options.currency || "$",
      confirmClearMessage: options.confirmClearMessage || "¿Estás seguro de que quieres vaciar el carrito?",
      emptyCartMessage: options.emptyCartMessage || "Carrito vacío",
      feedbackDuration: options.feedbackDuration || 2000,
      animationDuration: options.animationDuration || 200,
      ...options,
    }

    // Referencias a elementos DOM
    this.elements = {
      cartBtn: null,
      cartCount: null,
      cartSummary: null,
      cartItems: null,
      cartTotal: null,
    }

    // Estado del carrito
    this.isOpen = false

    // Inicializar cuando el DOM esté listo
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => this.init())
    } else {
      this.init()
    }
  }

  /**
   * Inicializar el componente
   */
  init() {
    this.bindElements()
    this.setupEventListeners()
    this.updateDisplay()
  }

  /**
   * Vincular elementos del DOM
   */
  bindElements() {
    this.elements.cartBtn = document.getElementById("cart-btn")
    this.elements.cartCount = document.getElementById("cart-count")
    this.elements.cartSummary = document.getElementById("cart-summary")
    this.elements.cartItems = document.getElementById("cart-items")
    this.elements.cartTotal = document.getElementById("cart-total")
    
    // Elementos de botones del carrito
    this.elements.btnCloseCart = document.getElementById("btn-close-cart")
    this.elements.btnClearCart = document.getElementById("btn-clear-cart")
    this.elements.btnCheckout = document.getElementById("btn-checkout")

    // Verificar que todos los elementos principales existan
    const requiredElements = ['cartBtn', 'cartCount', 'cartSummary', 'cartItems', 'cartTotal']
    const missingRequired = requiredElements.filter(key => !this.elements[key])

    if (missingRequired.length > 0) {
      console.warn("⚠️ Missing required cart elements:", missingRequired)
    }

    // Verificar elementos opcionales de botones
    const buttonElements = ['btnCloseCart', 'btnClearCart', 'btnCheckout']
    const missingButtons = buttonElements.filter(key => !this.elements[key])
    
    if (missingButtons.length > 0) {
      console.warn("⚠️ Missing cart button elements:", missingButtons)
    }
  }

  /**
   * Configurar event listeners
   */
  setupEventListeners() {
    // Event listener para el botón del carrito
    if (this.elements.cartBtn) {
      this.elements.cartBtn.addEventListener("click", (e) => {
        e.stopPropagation()
        this.toggle()
      })
    }

    // Event listener para cerrar carrito
    if (this.elements.btnCloseCart) {
      this.elements.btnCloseCart.addEventListener("click", () => this.close())
    }

    // Event listener para vaciar carrito
    if (this.elements.btnClearCart) {
      this.elements.btnClearCart.addEventListener("click", () => this.clear())
    }

    // Event listener para checkout
    if (this.elements.btnCheckout) {
      this.elements.btnCheckout.addEventListener("click", (e) => {
        e.preventDefault()
        window.location.href = '/checkout/'
      })
    }

    // Event listener para cerrar al hacer click fuera
    document.body.addEventListener("click", (e) => {
      if (this.isOpen && !this.elements.cartSummary?.contains(e.target) && !this.elements.cartBtn?.contains(e.target)) {
        this.close()
      }
    })

    // Prevenir que el click dentro del carrito lo cierre
    if (this.elements.cartSummary) {
      this.elements.cartSummary.addEventListener("click", (e) => {
        e.stopPropagation()
      })
    }

    // Event listeners para botones "Agregar al carrito"
    this.setupAddToCartButtons()
  }

  /**
   * Configurar botones "Agregar al carrito"
   */
  setupAddToCartButtons() {
    const addToCartButtons = document.querySelectorAll(".add-to-cart-btn")
    addToCartButtons.forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault()
        if (!btn.disabled) {
          const productData = {
            id: btn.dataset.id,
            nombre: btn.dataset.nombre,
            precio: Number.parseFloat(btn.dataset.precio),
          }
          this.addItem(productData)
        }
      })
    })
  }

  /**
   * Obtener carrito del localStorage
   */
  getCart() {
    try {
      return JSON.parse(localStorage.getItem(this.config.storageKey) || "{}")
    } catch (error) {
      console.error("Error parsing cart data:", error)
      return {}
    }
  }

  /**
   * Guardar carrito en localStorage
   */
  saveCart(cart) {
    try {
      localStorage.setItem(this.config.storageKey, JSON.stringify(cart))
    } catch (error) {
      console.error("Error saving cart data:", error)
    }
  }

  /**
   * Agregar item al carrito
   */
  addItem(product) {
    const cart = this.getCart()
    const { id, nombre, precio } = product

    if (!cart[id]) {
      cart[id] = { nombre, precio, cantidad: 1 }
    } else {
      cart[id].cantidad += 1
    }

    this.saveCart(cart)
    this.updateDisplay()
    this.showFeedback(`${nombre} agregado al carrito`)

    // Dispatch custom event
    this.dispatchEvent("itemAdded", { product, cart })
  }

  /**
   * Remover item del carrito
   */
  removeItem(id) {
    const cart = this.getCart()
    const item = cart[id]

    if (item) {
      delete cart[id]
      this.saveCart(cart)
      this.updateDisplay()
      this.showFeedback(`${item.nombre} eliminado del carrito`)

      // Dispatch custom event
      this.dispatchEvent("itemRemoved", { itemId: id, cart })
    }
  }

  /**
   * Actualizar cantidad de un item
   */
  updateItemQuantity(id, newQuantity) {
    const cart = this.getCart()

    if (cart[id]) {
      if (newQuantity <= 0) {
        this.removeItem(id)
      } else {
        cart[id].cantidad = Number.parseInt(newQuantity)
        this.saveCart(cart)
        this.updateDisplay()

        // Dispatch custom event
        this.dispatchEvent("itemUpdated", { itemId: id, newQuantity, cart })
      }
    }
  }

  /**
   * Vaciar carrito
   */
  clear() {
    if (confirm(this.config.confirmClearMessage)) {
      localStorage.removeItem(this.config.storageKey)
      this.updateDisplay()
      this.showFeedback("Carrito vaciado")

      // Dispatch custom event
      this.dispatchEvent("cartCleared", {})
    }
  }

  /**
   * Obtener estadísticas del carrito
   */
  getStats() {
    const cart = this.getCart()
    let itemCount = 0
    let total = 0

    for (const id in cart) {
      const item = cart[id]
      itemCount += item.cantidad
      total += item.cantidad * item.precio
    }

    return {
      itemCount,
      total: Number.parseFloat(total.toFixed(2)),
      isEmpty: itemCount === 0,
      itemsData: cart,
    }
  }

  /**
   * Actualizar visualización del carrito
   */
  updateDisplay() {
    const stats = this.getStats()

    // Actualizar contador
    if (this.elements.cartCount) {
      this.elements.cartCount.textContent = stats.itemCount

      // Animar contador si hay items
      if (stats.itemCount > 0) {
        this.animateCounter()
      }
    }

    // Actualizar total
    if (this.elements.cartTotal) {
      this.elements.cartTotal.textContent = stats.total.toFixed(2)
    }

    // Actualizar lista de items
    this.updateItemsList(stats.itemsData)
  }

  /**
   * Actualizar lista de items en el carrito
   */
  updateItemsList(cart) {
    if (!this.elements.cartItems) return

    if (Object.keys(cart).length === 0) {
      this.elements.cartItems.innerHTML = `<li class="text-gray-500 text-center py-4">${this.config.emptyCartMessage}</li>`
      return
    }

    let itemsHtml = ""
    for (const id in cart) {
      const item = cart[id]
      const itemTotal = (item.precio * item.cantidad).toFixed(2)

      itemsHtml += `
                <li class="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-md">
                    <div class="flex-1">
                        <span class="text-sm font-medium text-gray-800">${this.escapeHtml(item.nombre)}</span>
                        <div class="text-xs text-gray-600">${this.config.currency}${item.precio} x ${item.cantidad}</div>
                    </div>
                    <div class="flex items-center space-x-2">
                        <span class="text-sm font-semibold text-gray-800">${this.config.currency}${itemTotal}</span>
                        <button onclick="cart.removeItem('${id}')" class="text-red-500 hover:text-red-700 transition-colors" title="Eliminar producto">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                            </svg>
                        </button>
                    </div>
                </li>
            `
    }

    this.elements.cartItems.innerHTML = itemsHtml
  }

  /**
   * Animar el contador del carrito
   */
  animateCounter() {
    if (this.elements.cartCount) {
      this.elements.cartCount.classList.add("animate-pulse")
      setTimeout(() => {
        this.elements.cartCount.classList.remove("animate-pulse")
      }, 1000)
    }
  }

  /**
   * Mostrar carrito
   */
  show() {
    if (!this.elements.cartSummary || this.isOpen) return

    this.elements.cartSummary.classList.remove("hidden")
    this.isOpen = true

    setTimeout(() => {
      this.elements.cartSummary.classList.remove("opacity-0", "scale-95")
      this.elements.cartSummary.classList.add("opacity-100", "scale-100")
    }, 10)

    // Dispatch custom event
    this.dispatchEvent("cartOpened", {})
  }

  /**
   * Ocultar carrito
   */
  close() {
    if (!this.elements.cartSummary || !this.isOpen) return

    this.elements.cartSummary.classList.remove("opacity-100", "scale-100")
    this.elements.cartSummary.classList.add("opacity-0", "scale-95")

    setTimeout(() => {
      this.elements.cartSummary.classList.add("hidden")
      this.isOpen = false
    }, this.config.animationDuration)

    // Dispatch custom event
    this.dispatchEvent("cartClosed", {})
  }

  /**
   * Alternar visibilidad del carrito
   */
  toggle() {
    if (this.isOpen) {
      this.close()
    } else {
      this.show()
    }
  }

  /**
   * Mostrar feedback visual
   */
  showFeedback(message, type = "success") {
    const colorClass = type === "success" ? "bg-green-500" : type === "error" ? "bg-red-500" : "bg-blue-500"

    const feedback = document.createElement("div")
    feedback.className = `fixed top-20 right-4 ${colorClass} text-white px-4 py-2 rounded-md shadow-lg z-50 transform transition-all duration-300 translate-x-full`
    feedback.textContent = message
    document.body.appendChild(feedback)

    // Animar entrada
    setTimeout(() => {
      feedback.classList.remove("translate-x-full")
    }, 100)

    // Animar salida y remover
    setTimeout(() => {
      feedback.classList.add("translate-x-full")
      setTimeout(() => {
        if (document.body.contains(feedback)) {
          document.body.removeChild(feedback)
        }
      }, 300)
    }, this.config.feedbackDuration)
  }

  /**
   * Escapar HTML para prevenir XSS
   */
  escapeHtml(text) {
    const div = document.createElement("div")
    div.textContent = text
    return div.innerHTML
  }

  /**
   * Dispatch custom events
   */
  dispatchEvent(eventName, detail) {
    const event = new CustomEvent(`cart:${eventName}`, {
      detail,
      bubbles: true,
    })
    document.dispatchEvent(event)
  }

  /**
   * Métodos públicos para uso externo
   */

  // Obtener información del carrito
  getCartInfo() {
    return {
      items: this.getCart(),
      stats: this.getStats(),
      isOpen: this.isOpen,
    }
  }

  // Configurar callback para checkout
  onCheckout(callback) {
    if (typeof callback === "function") {
      this.checkoutCallback = callback
    }
  }

  // Ejecutar checkout
  checkout() {
    const cartData = this.getCartInfo()
    if (cartData.stats.isEmpty) {
      this.showFeedback("El carrito está vacío", "error")
      return
    }

    if (this.checkoutCallback) {
      this.checkoutCallback(cartData)
    } else {
      console.log("🛒 Checkout triggered:", cartData)
      this.dispatchEvent("checkoutRequested", cartData)
    }
  }

  /**
   * Función de debug para probar el checkout manualmente
   */
  debugCheckout() {
    console.log('🛒 Debug: Probando checkout...')
    console.log('🛒 Botón checkout:', this.elements.btnCheckout)
    if (this.elements.btnCheckout) {
      console.log('🛒 Redirigiendo a checkout...')
      window.location.href = '/checkout/'
    } else {
      console.error('🛒 Error: Botón checkout no encontrado')
    }
  }
}

// Funciones globales para compatibilidad con el HTML existente
function closeCart() {
  if (window.cart) {
    window.cart.close()
  }
}

function clearCart() {
  if (window.cart) {
    window.cart.clear()
  }
}

function removeFromCart(id) {
  if (window.cart) {
    window.cart.removeItem(id)
  }
}

// Exponer funciones globalmente
window.closeCart = closeCart
window.clearCart = clearCart
window.removeFromCart = removeFromCart

// Función de debug para probar checkout
function debugCheckout() {
  if (window.cart) {
    window.cart.debugCheckout()
  } else {
    console.error('🛒 Error: Carrito no inicializado')
  }
}

// Exponer función de debug globalmente
window.debugCheckout = debugCheckout

// Inicializar carrito automáticamente y exponerlo globalmente
// Asegurarse de que el DOM esté listo antes de inicializar
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    window.cart = new ShoppingCart()
  })
} else {
  window.cart = new ShoppingCart()
}

// Exponer la clase para uso avanzado
window.ShoppingCart = ShoppingCart

// Función simple para verificar estado (disponible globalmente)
window.verificarCarrito = function() {
  console.log('🛒 Estado del carrito:', {
    carritoExiste: !!window.cart,
    scriptCargado: !!window.cartScriptLoaded,
    claseDisponible: typeof window.ShoppingCart,
    elementosEncontrados: window.cart ? {
      cartBtn: !!window.cart.elements.cartBtn,
      btnCheckout: !!window.cart.elements.btnCheckout
    } : 'Carrito no existe'
  })
  
  // Intentar encontrar manualmente el botón de checkout
  const btn = document.getElementById('btn-checkout')
  console.log('🛒 Botón checkout en DOM:', btn)
  
  return {
    cart: window.cart,
    button: btn
  }
}
