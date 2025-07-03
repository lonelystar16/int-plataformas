# Documentación JavaScript - Ferramas Store

## 📁 Estructura de Archivos JavaScript

```
app/static/js/
├── utils.js         # Utilidades comunes compartidas
├── checkout.js      # Lógica del carrito y checkout
├── voucher.js       # Lógica del voucher de pago
├── cart.js          # Componente del carrito de compras
├── login.js         # Lógica del formulario de login
├── main.js          # Funcionalidades principales
├── subscriptionPopup.js  # Popup de suscripción
└── pago_redirect.js # Redirección de pagos
```

## 🛠️ Archivos JavaScript

### 1. `utils.js` - Utilidades Comunes
**Propósito:** Funciones utilitarias compartidas entre módulos

**Funciones principales:**
- `FerramasUtils.formatearMoneda(valor)` - Formatea números como moneda chilena
- `FerramasUtils.escapeHtml(text)` - Previene ataques XSS
- `FerramasUtils.getCookie(name)` - Obtiene cookies (útil para CSRF)
- `FerramasUtils.setElementText(id, text)` - Establece texto de elementos
- `FerramasUtils.validarEmail(email)` - Valida formato de email
- `FerramasUtils.formatearFecha(fecha)` - Formatea fechas en formato chileno
- `FerramasUtils.truncarTexto(text, max)` - Trunca texto con "..."
- `FerramasUtils.copiarAlPortapapeles(text)` - Copia texto al portapapeles

**Uso:**
```javascript
// Formatear moneda
const precio = FerramasUtils.formatearMoneda(15000); // "$15.000"

// Validar email
const esValido = FerramasUtils.validarEmail("test@example.com"); // true
```

### 2. `checkout.js` - Gestión del Checkout
**Propósito:** Maneja el carrito de compras y procesamiento de pagos

**Clase principal:** `CheckoutManager`

**Funciones principales:**
- `loadCart()` - Carga carrito desde localStorage
- `renderCart()` - Renderiza elementos del carrito
- `updateTotal()` - Calcula y muestra totales con descuentos
- `procesarPago(metodo)` - Procesa pagos (tarjeta/transferencia)
- `validarYProcesarPago()` - Valida datos de clientes invitados
- `toggleTransferDetails()` - Muestra/oculta detalles de transferencia

**Event Listeners configurados:**
- `#btn-volver` - Navegación hacia atrás
- `#btn-continuar-pago` - Continuar con pago (invitados)
- `#transfer-button` - Toggle detalles transferencia
- `#pagar-tarjeta` - Procesar pago con tarjeta
- `#confirmar-transferencia` - Confirmar transferencia

**Integración con Django:**
```javascript
// Variables pasadas desde Django
window.discountPercentage = 10; // Porcentaje de descuento
window.isAuthenticated = true;  // Estado de autenticación
```

**Flujo de pago:**
1. Cargar carrito desde localStorage
2. Renderizar productos y calcular totales
3. Validar datos del cliente (si no está autenticado)
4. Enviar petición AJAX a `/procesar-pago/`
5. Redirigir al voucher con token único

### 3. `voucher.js` - Gestión del Voucher
**Propósito:** Muestra y formatea el voucher de pago

**Clase principal:** `VoucherManager`

**Funciones principales:**
- `cargarVoucher(datos)` - Carga datos del voucher en la interfaz
- `cargarTotales(datos)` - Renderiza sección de totales
- `cargarProductos(productos)` - Renderiza tabla de productos
- `crearFilaProducto(producto)` - Genera HTML de fila de producto
- `mostrarAccesoDenegado()` - Muestra mensaje de error de acceso
- `cargarDesdeSessionStorage()` - Fallback para datos en sessionStorage

**Integración con Django:**
```javascript
// Datos pasados desde Django
window.voucherData = {
    numero_voucher: 'FRS20240001',
    comprador: 'Juan Pérez',
    total: 15000,
    productos: [...],
    // ... otros datos
};
```

**Funciones globales:**
- `imprimirVoucher()` - Imprime el voucher
- `volverAlInicio()` - Redirige al home

### 4. `cart.js` - Componente de Carrito
**Propósito:** Componente reutilizable para el carrito de compras

**Clase principal:** `ShoppingCart`

**Funciones principales:**
- `bindElements()` - Vincula elementos del DOM
- `setupEventListeners()` - Configura event listeners
- `open()/close()/toggle()` - Control de visibilidad del carrito
- `addItem(id, producto)` - Añade producto al carrito
- `removeItem(id)` - Elimina producto del carrito
- `clear()` - Vacía el carrito completo
- `updateDisplay()` - Actualiza contador y vista del carrito

**Event Listeners configurados:**
- `#cart-btn` - Toggle del carrito
- `#btn-close-cart` - Cerrar carrito
- `#btn-clear-cart` - Vaciar carrito
- `#btn-checkout` - Ir a checkout
- Botones "Agregar al carrito" - Automáticamente detectados

**Configuración:**
```javascript
const cart = new ShoppingCart({
    storageKey: "cart",
    currency: "$",
    confirmClearMessage: "¿Estás seguro de que quieres vaciar el carrito?",
    emptyCartMessage: "Carrito vacío"
});
```

### 5. `login.js` - Formulario de Login
**Propósito:** Maneja la funcionalidad del formulario de login

**Clase principal:** `LoginManager`

**Funciones principales:**
- `setupPasswordToggle()` - Configura toggle de visibilidad de contraseña
- `preserveUserInput()` - Preserva el input del usuario en caso de error

**Event Listeners configurados:**
- `#togglePassword` - Toggle visibilidad de contraseña

**Elementos requeridos en HTML:**
- `#togglePassword` - Botón de toggle
- `#password` - Campo de contraseña
- `#eyeIconOpen` - Icono de ojo abierto
- `#eyeIconClosed` - Icono de ojo cerrado
- `#usuario` - Campo de usuario

## 🔧 Configuración en Templates

### Checkout Template
```django
{% load static %}
<!-- Pasar configuración a JavaScript -->
<script>
    window.discountPercentage = {{ discount_percentage|default:0 }};
    window.isAuthenticated = {{ user.is_authenticated|yesno:"true,false" }};
</script>

<!-- Cargar archivos JS -->
<script src="{% static 'js/utils.js' %}"></script>
<script src="{% static 'js/checkout.js' %}"></script>
```

### Voucher Template
```django
{% load static %}
<!-- Pasar datos del voucher a JavaScript -->
<script>
    {% if voucher_data %}
    window.voucherData = {
        numero_voucher: '{{ voucher_data.numero_voucher }}',
        // ... otros datos
    };
    {% endif %}
</script>

<!-- Cargar archivos JS -->
<script src="{% static 'js/utils.js' %}"></script>
<script src="{% static 'js/voucher.js' %}"></script>
```

### Login Template
```django
{% load static %}
<!-- Cargar archivos JS -->
<script src="{% static 'js/login.js' %}"></script>
```

### Templates con Carrito (Base/Components)
```django
{% load static %}
<!-- Cargar componente de carrito -->
<script src="{% static 'js/utils.js' %}"></script>
<script src="{% static 'js/cart.js' %}"></script>

<!-- Incluir componente HTML del carrito -->
{% include 'components/cart.html' %}
```

### Templates Principales
```django
{% load static %}
<!-- Cargar funcionalidades principales -->
<script src="{% static 'js/utils.js' %}"></script>
<script src="{% static 'js/main.js' %}"></script>
<script src="{% static 'js/cart.js' %}"></script>
```

## 📋 Beneficios de la Separación

### ✅ **Ventajas:**

1. **Mantenibilidad:** Código organizado en módulos específicos
2. **Reutilización:** Utilidades comunes disponibles en toda la app
3. **Debugging:** Errores más fáciles de localizar
4. **Performance:** Archivos pueden ser cacheados por el navegador
5. **Legibilidad:** Templates más limpios y enfocados en HTML
6. **Escalabilidad:** Fácil agregar nuevas funcionalidades
7. **Testing:** JavaScript separado es más fácil de testear

### 🔄 **Patrón de Comunicación:**

```
Django Template → window.variableGlobal → JavaScript Module
```

### 🚀 **Extensibilidad:**

Para agregar nuevas funcionalidades:

1. **Crear nuevo archivo JS** en `/static/js/`
2. **Definir clase** con funciones específicas
3. **Cargar en template** con `{% static 'js/nuevo-archivo.js' %}`
4. **Usar utilidades** de `FerramasUtils` cuando sea necesario

## 🐛 Debugging

### Console Logs:
Los archivos JS incluyen logs para debugging:
```javascript
console.error('[Ferramas]', 'Error message');
```

### Variables Globales Disponibles:
- `window.checkoutManager` - Instancia del gestor de checkout
- `window.voucherManager` - Instancia del gestor de voucher
- `window.FerramasUtils` - Utilidades comunes
- `window.voucherData` - Datos del voucher (solo en voucher.html)
- `window.discountPercentage` - Porcentaje de descuento (solo en checkout.html)
- `window.isAuthenticated` - Estado de autenticación (solo en checkout.html)

## 📈 Performance

### Optimizaciones implementadas:
- **Lazy loading:** JavaScript se carga solo cuando es necesario
- **Event delegation:** Listeners eficientes
- **DOM queries mínimas:** Cache de elementos frecuentemente usados
- **Error handling:** Prevención de crashes por errores JS

Esta estructura modular facilita el mantenimiento y permite un desarrollo más organizado del frontend.
