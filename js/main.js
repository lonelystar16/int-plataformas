// Esperar a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    // Función para manejar el menú móvil (se implementará más adelante)
    function handleMobileMenu() {
        // Código para el menú móvil
    }

    // Función para añadir efectos de hover a las tarjetas
    const cards = document.querySelectorAll('.bg-white.rounded-lg');
    cards.forEach(card => {
        card.classList.add('hover-scale');
    });

    // Función para validar formularios (se implementará cuando se agreguen formularios)
    function validateForm(event) {
        // Código de validación
    }

    // Función para mostrar mensajes de alerta personalizados
    function showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `fixed top-4 right-4 p-4 rounded-lg ${
            type === 'error' ? 'bg-red-500' : 
            type === 'success' ? 'bg-green-500' : 
            'bg-blue-500'
        } text-white`;
        alertDiv.textContent = message;
        
        document.body.appendChild(alertDiv);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 3000);
    }

    // Ejemplo de uso del sistema de alertas
    // showAlert('¡Bienvenido a Ferramas!', 'success');
}); 