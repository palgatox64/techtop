document.addEventListener('DOMContentLoaded', function () {
    // Seleccionamos todos los botones que tengan la clase 'btn-delete-item'
    const deleteButtons = document.querySelectorAll('.btn-delete-item');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            event.preventDefault(); // Prevenimos la acción por defecto

            // Obtenemos los datos del botón
            const url = this.dataset.url;
            const itemName = this.dataset.itemName;
            const csrfToken = this.dataset.csrfToken;

            // Mostramos la primera alerta de confirmación
            Swal.fire({
                title: `¿Estás seguro de que quieres eliminar "${itemName}"?`,
                text: "¡Esta acción no se puede revertir!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'No, cancelar'
            }).then((result) => {
                // Si el usuario confirma...
                if (result.isConfirmed) {
                    // Enviamos la petición de eliminación al servidor
                    fetch(url, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrfToken,
                            'Content-Type': 'application/json'
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // Si el servidor confirma la eliminación, mostramos la alerta de éxito
                            Swal.fire({
                                title: '¡Eliminado!',
                                text: data.message,
                                icon: 'success',
                                timer: 2000,
                                showConfirmButton: false
                            }).then(() => {
                                // Recargamos la página para que la tabla se actualice
                                location.reload();
                            });
                        } else {
                            // Si hay un error en el servidor
                            Swal.fire('Error', data.message, 'error');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        Swal.fire('Error de Conexión', 'No se pudo comunicar con el servidor.', 'error');
                    });
                }
            });
        });
    });
});