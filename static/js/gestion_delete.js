document.addEventListener('DOMContentLoaded', function () {
    
    const deleteButtons = document.querySelectorAll('.btn-delete-item');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            event.preventDefault(); 

            
            const url = this.dataset.url;
            const itemName = this.dataset.itemName;
            const csrfToken = this.dataset.csrfToken;

            
            Swal.fire({
                title: `¿Estás seguro de que quieres eliminar "${itemName}"?`,
                text: "¡Esta acción no se puede revertir!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'No, cancelar'
            }).then((result) => {
                
                if (result.isConfirmed) {
                    
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
                            
                            Swal.fire({
                                title: '¡Eliminado!',
                                text: data.message,
                                icon: 'success',
                                timer: 2000,
                                showConfirmButton: false
                            }).then(() => {
                                
                                location.reload();
                            });
                        } else {
                            
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
