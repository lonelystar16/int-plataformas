// Script para mostrar y ocultar el pop-up
document.addEventListener('DOMContentLoaded', function() {
    const popupOverlay = document.getElementById('subscription-popup-overlay');
    const closeButton = document.getElementById('close-popup');
    const subscribeButton = popupOverlay ? popupOverlay.querySelector('button[type="submit"]') : null; // Obtener referencia al botón de suscripción

    // Solo ejecutar si el pop-up existe en el HTML (usuario no autenticado)
    if (popupOverlay && subscribeButton) {
        const hasClosedPopup = localStorage.getItem('subscriptionPopupClosed');

        // Mostrar el pop-up solo si no ha sido cerrado antes
        if (!hasClosedPopup) {
             popupOverlay.classList.remove('hidden'); // Mostrar el pop-up removiendo la clase hidden

            // Función para ocultar el pop-up y guardar la preferencia
            const hidePopupAndSetPreference = () => {
                popupOverlay.classList.add('hidden');
                localStorage.setItem('subscriptionPopupClosed', 'true');
            };

            // Ocultar el pop-up y guardar preferencia al hacer clic en el botón de cerrar
            closeButton.addEventListener('click', hidePopupAndSetPreference);

            // Ocultar el pop-up al hacer clic fuera del contenido (opcional)
            popupOverlay.addEventListener('click', function(event) {
                // Verificamos si el clic fue directamente en el overlay y no en el contenido del pop-up
                if (event.target === popupOverlay) {
                    hidePopupAndSetPreference();
                }
            });

            // Ocultar el pop-up y guardar preferencia al hacer clic en el botón de suscripción
            subscribeButton.addEventListener('click', function(event) {
                event.preventDefault(); // Prevenir el comportamiento por defecto del botón de submit
                hidePopupAndSetPreference();
            });
        } else {
            // Si ya ha sido cerrado, el pop-up ya tiene la clase 'hidden' en el HTML, así que no hacemos nada aquí.
            // popupOverlay.classList.add('hidden'); // Esta línea ya no es necesaria
        }
    }
}); 