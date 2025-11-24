/**
 * Función para alternar la visibilidad de las contraseñas
 * @param {string} fieldId - ID del campo de contraseña
 */
function togglePassword(fieldId) {
    const passwordField = document.getElementById(fieldId);
    const toggleIcon = document.getElementById(fieldId + '-toggle-icon');
    
    if (!passwordField || !toggleIcon) {
        console.error(`No se encontró el campo ${fieldId} o su icono`);
        return;
    }
    
    // Alternar el tipo de input
    if (passwordField.type === 'password') {
        passwordField.type = 'text';
        toggleIcon.className = 'bx bx-show';
        toggleIcon.setAttribute('title', 'Ocultar contraseña');
    } else {
        passwordField.type = 'password';
        toggleIcon.className = 'bx bx-hide';
        toggleIcon.setAttribute('title', 'Mostrar contraseña');
    }
}

// Configurar los tooltips iniciales cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Configurar tooltips para todos los toggles de contraseña
    const passwordToggles = document.querySelectorAll('.password-toggle');
    
    passwordToggles.forEach(toggle => {
        const icon = toggle.querySelector('i');
        if (icon && icon.classList.contains('bx-hide')) {
            icon.setAttribute('title', 'Mostrar contraseña');
        }
    });
    
    // Agregar eventos de teclado para mejorar la accesibilidad
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('keydown', function(e) {
            // Permitir activar con Enter o Espacio
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
        
        // Hacer el botón focusable
        toggle.setAttribute('tabindex', '0');
    });
});

// Función adicional para mejorar la experiencia de usuario
function initPasswordToggles() {
    const toggles = document.querySelectorAll('.password-toggle');
    
    toggles.forEach(toggle => {
        // Añadir efecto visual al hacer hover
        toggle.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-50%) scale(1.1)';
        });
        
        toggle.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(-50%) scale(1)';
        });
        
        // Añadir efecto de "click" visual
        toggle.addEventListener('mousedown', function() {
            this.style.transform = 'translateY(-50%) scale(0.95)';
        });
        
        toggle.addEventListener('mouseup', function() {
            this.style.transform = 'translateY(-50%) scale(1.1)';
        });
    });
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', initPasswordToggles);