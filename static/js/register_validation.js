document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('register-form');
    const submitBtn = document.getElementById('submit-btn');
    
    // Objeto para rastrear el estado de validación de cada campo
    const validationState = {
        nombre: false,
        apellido: false,
        correo: false,
        telefono: false,
        password: false,
        password2: false
    };

    // Función para actualizar el estado del botón
    function updateSubmitButton() {
        const allValid = Object.values(validationState).every(valid => valid === true);
        submitBtn.disabled = !allValid;
        
        if (allValid) {
            submitBtn.textContent = 'Registrarse';
            submitBtn.style.background = '#2c2c2c'; /* CAMBIADO: Negro en lugar del gradiente */
            submitBtn.style.color = '#fff'; /* CAMBIADO: Texto blanco */
        } else {
            submitBtn.textContent = 'Registrarse';
            submitBtn.style.background = '#e9ecef';
            submitBtn.style.color = '#6c757d';
        }
    }

    // Función para mostrar estado de validación visual
    function setFieldValidation(fieldId, isValid, iconType = null) {
        const field = document.getElementById(fieldId);
        const icon = document.getElementById(fieldId + '-icon');
        
        // Remover clases previas
        field.classList.remove('valid', 'invalid');
        icon.classList.remove('valid', 'invalid');
        
        if (iconType !== null) {
            if (isValid) {
                field.classList.add('valid');
                icon.classList.add('valid');
                icon.innerHTML = '✓';
            } else {
                field.classList.add('invalid');
                icon.classList.add('invalid');
                icon.innerHTML = '✗';
            }
        } else {
            icon.innerHTML = '';
        }
        
        validationState[fieldId] = isValid;
        updateSubmitButton();
    }

    // Manejar tooltips con eventos de focus/blur
    function setupTooltipEvents() {
        const inputs = ['nombre', 'apellido', 'correo', 'telefono', 'password', 'password2'];
        
        inputs.forEach(inputId => {
            const input = document.getElementById(inputId);
            const tooltip = document.getElementById(inputId + '-tooltip');
            
            // Mostrar tooltip al hacer focus
            input.addEventListener('focus', function() {
                // Ocultar todos los otros tooltips
                inputs.forEach(otherId => {
                    if (otherId !== inputId) {
                        const otherTooltip = document.getElementById(otherId + '-tooltip');
                        otherTooltip.style.opacity = '0';
                        otherTooltip.style.visibility = 'hidden';
                        otherTooltip.style.transform = 'translateY(10px)';
                    }
                });
                
                // Mostrar el tooltip actual
                setTimeout(() => {
                    tooltip.style.opacity = '1';
                    tooltip.style.visibility = 'visible';
                    tooltip.style.transform = 'translateY(0)';
                }, 50);
            });
            
            // Ocultar tooltip al perder focus (después de un delay)
            input.addEventListener('blur', function() {
                setTimeout(() => {
                    tooltip.style.opacity = '0';
                    tooltip.style.visibility = 'hidden';
                    tooltip.style.transform = 'translateY(10px)';
                }, 200);
            });
        });
    }

    // Validaciones en tiempo real
    document.getElementById('nombre').addEventListener('input', function() {
        const value = this.value.trim();
        const nameRegex = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/;
        const isValid = value.length >= 2 && nameRegex.test(value);
        setFieldValidation('nombre', isValid, value.length > 0);
    });

    document.getElementById('apellido').addEventListener('input', function() {
        const value = this.value.trim();
        const nameRegex = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/;
        const isValid = value.length >= 2 && nameRegex.test(value);
        setFieldValidation('apellido', isValid, value.length > 0);
    });

    document.getElementById('correo').addEventListener('input', function() {
        const value = this.value.trim();
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        const isValid = emailRegex.test(value);
        setFieldValidation('correo', isValid, value.length > 0);
    });

    document.getElementById('telefono').addEventListener('input', function() {
        const value = this.value.trim();
        const phoneRegex = /^9\d{8}$/;
        const isValid = phoneRegex.test(value);
        setFieldValidation('telefono', isValid, value.length > 0);
    });

    document.getElementById('password').addEventListener('input', function() {
        const value = this.value;
        const isValid = value.length >= 8 && 
                       /[a-z]/.test(value) && 
                       /[A-Z]/.test(value) && 
                       /\d/.test(value) && 
                       /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~`]/.test(value) &&
                       !/['"\\]/.test(value);
        setFieldValidation('password', isValid, value.length > 0);
        
        // Re-validar confirmación de contraseña si ya tiene contenido
        const password2 = document.getElementById('password2').value;
        if (password2.length > 0) {
            const password2Valid = value === password2 && isValid;
            setFieldValidation('password2', password2Valid, true);
        }
    });

    document.getElementById('password2').addEventListener('input', function() {
        const value = this.value;
        const password = document.getElementById('password').value;
        const isValid = value === password && value.length > 0 && validationState.password;
        setFieldValidation('password2', isValid, value.length > 0);
    });

    // Manejo del envío del formulario
    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const nombre = document.getElementById('nombre').value.trim();
        const apellido = document.getElementById('apellido').value.trim();
        const correo = document.getElementById('correo').value.trim();
        const telefono = document.getElementById('telefono').value.trim();
        const password = document.getElementById('password').value;
        const password2 = document.getElementById('password2').value;

        // Validación final (por si acaso)
        if (!Object.values(validationState).every(valid => valid === true)) {
            Swal.fire({
                icon: 'error',
                title: 'Formulario incompleto',
                text: 'Por favor, completa correctamente todos los campos antes de continuar.',
            });
            return;
        }

        // Deshabilitar botón durante el envío
        submitBtn.disabled = true;
        submitBtn.textContent = 'Enviando...';

        Swal.fire({
            icon: 'success',
            title: 'Validación correcta',
            text: 'Enviando datos...',
            timer: 1500, 
            showConfirmButton: false
        }).then(() => {
            form.submit(); 
        });
    });

    // Inicializar tooltips y estado del botón
    setupTooltipEvents();
    updateSubmitButton();
});