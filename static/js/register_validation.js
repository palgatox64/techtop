document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('register-form');

    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const nombre = document.getElementById('nombre').value.trim();
        const apellido = document.getElementById('apellido').value.trim();
        const correo = document.getElementById('correo').value.trim();
        const telefono = document.getElementById('telefono').value.trim();
        const password = document.getElementById('password').value;
        const password2 = document.getElementById('password2').value;

        if (!nombre || !apellido || !correo || !telefono || !password || !password2) {
            Swal.fire({ icon: 'error', title: 'Oops...', text: 'Por favor, completa todos los campos.' });
            return;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(correo)) {
            Swal.fire({ icon: 'error', title: 'Correo Inválido', text: 'Por favor, ingresa una dirección de correo electrónico válida.' });
            return;
        }

        if (password !== password2) {
            Swal.fire({ icon: 'error', title: 'Contraseñas no coinciden', text: 'Asegúrate de que ambas contraseñas sean iguales.' });
            return;
        }

        const passwordRegex = /^(?=.*[A-Z])(?=.*\d).{8,}$/;
        if (!passwordRegex.test(password)) {
            Swal.fire({ icon: 'error', title: 'Contraseña no segura', html: 'La contraseña debe tener al menos:<br>- 8 caracteres<br>- Una mayúscula<br>- Un número' });
            return;
        }

        const phoneRegex = /^\d{9}$/;
        if (!phoneRegex.test(telefono)) {
            Swal.fire({ icon: 'error', title: 'Número de teléfono inválido', text: 'El teléfono debe tener exactamente 9 dígitos y contener solo números.' });
            return;
        }

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
});