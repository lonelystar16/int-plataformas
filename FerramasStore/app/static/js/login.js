/**
 * Login Form Management - Ferramas Store
 * Maneja la funcionalidad del formulario de login
 */

class LoginManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupPasswordToggle();
        this.preserveUserInput();
    }

    /**
     * Preserva el input del usuario en caso de error de login
     */
    preserveUserInput() {
        const usuarioInput = document.getElementById('usuario');
        const formElement = document.querySelector('form');

        if (formElement && formElement.dataset.usuario && usuarioInput) {
            usuarioInput.value = formElement.dataset.usuario;
        }
    }

    /**
     * Configura el toggle de visibilidad de contraseña
     */
    setupPasswordToggle() {
        const togglePassword = document.getElementById('togglePassword');
        const passwordInput = document.getElementById('password');
        const eyeIconOpen = document.getElementById('eyeIconOpen');
        const eyeIconClosed = document.getElementById('eyeIconClosed');

        if (togglePassword && passwordInput && eyeIconOpen && eyeIconClosed) {
            togglePassword.addEventListener('click', () => {
                const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
                passwordInput.setAttribute('type', type);

                eyeIconOpen.classList.toggle('hidden');
                eyeIconClosed.classList.toggle('hidden');
            });
        }
    }
}

// Auto-inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    new LoginManager();
});
