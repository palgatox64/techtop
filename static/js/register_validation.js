document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('register-form');
    const submitBtn = document.getElementById('submit-btn');
    
    
    const validationState = {
        rut: false,
        nombre: false,
        apellido: false,
        correo: false,
        telefono: false,
        password: false,
        password2: false
    };

    
    function updateSubmitButton() {
        const allValid = Object.values(validationState).every(valid => valid === true);
        submitBtn.disabled = !allValid;
        
        if (allValid) {
            submitBtn.textContent = 'Registrarse';
            submitBtn.style.background = '#2c2c2c'; 
            submitBtn.style.color = '#fff'; 
        } else {
            submitBtn.textContent = 'Registrarse';
            submitBtn.style.background = '#e9ecef';
            submitBtn.style.color = '#6c757d';
        }
    }

    
    function setFieldValidation(fieldId, isValid, iconType = null) {
        const field = document.getElementById(fieldId);
        const icon = document.getElementById(fieldId + '-icon');
        
        
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

    
    function setupTooltipEvents() {
        const inputs = ['rut', 'nombre', 'apellido', 'correo', 'telefono', 'password', 'password2'];
        
        inputs.forEach(inputId => {
            const input = document.getElementById(inputId);
            const tooltip = document.getElementById(inputId + '-tooltip');
            
            
            input.addEventListener('focus', function() {
                
                inputs.forEach(otherId => {
                    if (otherId !== inputId) {
                        const otherTooltip = document.getElementById(otherId + '-tooltip');
                        otherTooltip.style.opacity = '0';
                        otherTooltip.style.visibility = 'hidden';
                        otherTooltip.style.transform = 'translateY(10px)';
                    }
                });
                
                
                setTimeout(() => {
                    tooltip.style.opacity = '1';
                    tooltip.style.visibility = 'visible';
                    tooltip.style.transform = 'translateY(0)';
                }, 50);
            });
            
            
            input.addEventListener('blur', function() {
                setTimeout(() => {
                    tooltip.style.opacity = '0';
                    tooltip.style.visibility = 'hidden';
                    tooltip.style.transform = 'translateY(10px)';
                }, 200);
            });
        });
    }

    
    
    
    function validarRUT(rut) {
        
        rut = rut.replace(/\./g, '').replace(/-/g, '').toUpperCase();
        
        
        if (!/^\d{7,8}[0-9K]$/.test(rut)) {
            return false;
        }
        
        
        const numero = rut.slice(0, -1);
        const dvIngresado = rut.slice(-1);
        
        
        let suma = 0;
        let multiplicador = 2;
        
        for (let i = numero.length - 1; i >= 0; i--) {
            suma += parseInt(numero[i]) * multiplicador;
            multiplicador++;
            if (multiplicador > 7) {
                multiplicador = 2;
            }
        }
        
        const resto = suma % 11;
        let dvCalculado = 11 - resto;
        
        
        if (dvCalculado === 11) {
            dvCalculado = '0';
        } else if (dvCalculado === 10) {
            dvCalculado = 'K';
        } else {
            dvCalculado = dvCalculado.toString();
        }
        
        
        return dvIngresado === dvCalculado;
    }
    
    
    function formatearRUT(rut) {
        
        rut = rut.replace(/[^0-9kK]/g, '').toUpperCase();
        
        
        if (rut.length > 9) {
            rut = rut.slice(0, 9);
        }
        
        
        if (rut.length > 1) {
            rut = rut.slice(0, -1) + '-' + rut.slice(-1);
        }
        
        return rut;
    }
    
    document.getElementById('rut').addEventListener('input', function() {
        
        const cursorPosition = this.selectionStart;
        const oldLength = this.value.length;
        
        this.value = formatearRUT(this.value);
        
        const newLength = this.value.length;
        const newCursorPosition = cursorPosition + (newLength - oldLength);
        this.setSelectionRange(newCursorPosition, newCursorPosition);
        
        const value = this.value.trim();
        const isValid = validarRUT(value);
        setFieldValidation('rut', isValid, value.length > 0);
    });

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

    
    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const rut = document.getElementById('rut').value.trim();
        const nombre = document.getElementById('nombre').value.trim();
        const apellido = document.getElementById('apellido').value.trim();
        const correo = document.getElementById('correo').value.trim();
        const telefono = document.getElementById('telefono').value.trim();
        const password = document.getElementById('password').value;
        const password2 = document.getElementById('password2').value;

        
        if (!Object.values(validationState).every(valid => valid === true)) {
            Swal.fire({
                icon: 'error',
                title: 'Formulario incompleto',
                text: 'Por favor, completa correctamente todos los campos antes de continuar.',
            });
            return;
        }

        
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

    
    setupTooltipEvents();
    updateSubmitButton();
});
