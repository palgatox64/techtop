
function togglePassword(fieldId) {
    const passwordField = document.getElementById(fieldId);
    const toggleIcon = document.getElementById(fieldId + '-toggle-icon');
    
    if (!passwordField || !toggleIcon) {
        console.error(`No se encontró el campo ${fieldId} o su icono`);
        return;
    }
    
    
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


document.addEventListener('DOMContentLoaded', function() {
    
    const passwordToggles = document.querySelectorAll('.password-toggle');
    
    passwordToggles.forEach(toggle => {
        const icon = toggle.querySelector('i');
        if (icon && icon.classList.contains('bx-hide')) {
            icon.setAttribute('title', 'Mostrar contraseña');
        }
    });
    
    
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('keydown', function(e) {
            
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
        
        
        toggle.setAttribute('tabindex', '0');
    });
});


function initPasswordToggles() {
    const toggles = document.querySelectorAll('.password-toggle');
    
    toggles.forEach(toggle => {
        
        toggle.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-50%) scale(1.1)';
        });
        
        toggle.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(-50%) scale(1)';
        });
        
        
        toggle.addEventListener('mousedown', function() {
            this.style.transform = 'translateY(-50%) scale(0.95)';
        });
        
        toggle.addEventListener('mouseup', function() {
            this.style.transform = 'translateY(-50%) scale(1.1)';
        });
    });
}


document.addEventListener('DOMContentLoaded', initPasswordToggles);
