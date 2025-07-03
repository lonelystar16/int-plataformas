/**
 * Common Utilities - Ferramas Store
 * Funciones utilitarias compartidas entre diferentes módulos
 */

class FerramasUtils {
    /**
     * Formatea un número como moneda chilena
     * @param {number} valor - Valor a formatear
     * @returns {string} Valor formateado
     */
    static formatearMoneda(valor) {
        return `$${Number(valor).toLocaleString('es-CL')}`;
    }

    /**
     * Escapa HTML para prevenir XSS
     * @param {string} text - Texto a escapar
     * @returns {string} Texto escapado
     */
    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Obtiene una cookie por nombre
     * @param {string} name - Nombre de la cookie
     * @returns {string|null} Valor de la cookie
     */
    static getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    /**
     * Establece el texto de un elemento por ID
     * @param {string} elementId - ID del elemento
     * @param {string} text - Texto a establecer
     */
    static setElementText(elementId, text) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = text;
        }
    }

    /**
     * Muestra un mensaje de error en la consola y opcionalmente al usuario
     * @param {string} mensaje - Mensaje de error
     * @param {boolean} mostrarAlUsuario - Si mostrar alert al usuario
     */
    static mostrarError(mensaje, mostrarAlUsuario = false) {
        console.error('[Ferramas]', mensaje);
        if (mostrarAlUsuario) {
            alert(mensaje);
        }
    }

    /**
     * Debounce function para limitar llamadas frecuentes
     * @param {Function} func - Función a ejecutar
     * @param {number} wait - Tiempo de espera en ms
     * @returns {Function} Función con debounce
     */
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Valida si un email tiene formato válido
     * @param {string} email - Email a validar
     * @returns {boolean} True si es válido
     */
    static validarEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    /**
     * Carga un script de forma asíncrona
     * @param {string} src - URL del script
     * @returns {Promise} Promise que se resuelve cuando el script se carga
     */
    static cargarScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    /**
     * Convierte un string a slug (URL friendly)
     * @param {string} str - String a convertir
     * @returns {string} Slug generado
     */
    static toSlug(str) {
        return str
            .toLowerCase()
            .replace(/[áàäâ]/g, 'a')
            .replace(/[éèëê]/g, 'e')
            .replace(/[íìïî]/g, 'i')
            .replace(/[óòöô]/g, 'o')
            .replace(/[úùüû]/g, 'u')
            .replace(/[ñ]/g, 'n')
            .replace(/[ç]/g, 'c')
            .replace(/[^a-z0-9]/g, '-')
            .replace(/-+/g, '-')
            .replace(/^-|-$/g, '');
    }

    /**
     * Copia texto al portapapeles
     * @param {string} text - Texto a copiar
     * @returns {Promise<boolean>} True si se copió exitosamente
     */
    static async copiarAlPortapapeles(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            console.error('Error al copiar al portapapeles:', err);
            return false;
        }
    }

    /**
     * Genera un ID único
     * @returns {string} ID único
     */
    static generarId() {
        return 'ferramas_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Formatea una fecha en formato chileno
     * @param {Date|string} fecha - Fecha a formatear
     * @returns {string} Fecha formateada
     */
    static formatearFecha(fecha) {
        const date = typeof fecha === 'string' ? new Date(fecha) : fecha;
        return date.toLocaleDateString('es-CL', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    /**
     * Trunca un texto a cierta cantidad de caracteres
     * @param {string} text - Texto a truncar
     * @param {number} maxLength - Longitud máxima
     * @returns {string} Texto truncado
     */
    static truncarTexto(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength).trim() + '...';
    }
}

// Hacer disponible globalmente
window.FerramasUtils = FerramasUtils;

// Alias para compatibilidad
window.Utils = FerramasUtils;
