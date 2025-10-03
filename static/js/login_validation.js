document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('login-form');

    form.addEventListener('submit', async function(event) {
        event.preventDefault(); // ¡AGREGAR ESTA LÍNEA QUE FALTA!

        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;

        if (!email || !password) {
            Swal.fire({
                icon: 'error',
                title: 'Campos incompletos',
                text: 'Por favor, ingresa tu correo y contraseña.',
            });
            return;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            Swal.fire({
                icon: 'error',
                title: 'Correo Inválido',
                text: 'Por favor, ingresa una dirección de correo válida.',
            });
            return;
        }

        try {
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrftoken,
                },
                body: new URLSearchParams({
                    'email': email,
                    'password': password,
                    'csrfmiddlewaretoken': csrftoken
                })
            });

            const data = await response.json();

            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: '¡Éxito!',
                    text: data.message,
                    timer: 3000,                    // Exactamente 3 segundos
                    showConfirmButton: false,       // No mostrar botón para que no interfiera
                    allowOutsideClick: false,       // No permitir cerrar haciendo clic afuera
                    allowEscapeKey: false           // No permitir cerrar con ESC
                }).then(() => {
                    // Esta función se ejecuta después de exactamente 3 segundos
                    window.location.href = data.redirect_url;
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error de login',
                    text: data.message,
                });
            }

        } catch (error) {
            console.error('Error al enviar la petición de login:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error de conexión',
                text: 'No se pudo conectar con el servidor. Intenta de nuevo más tarde.',
            });
        }
    });
});