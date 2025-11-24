document.addEventListener('DOMContentLoaded', function () {
    const trackingForm = document.getElementById('tracking-form');
    const resultsSection = document.getElementById('results-section');
    const orderInput = document.getElementById('order-input');
    const orderIdDisplay = document.getElementById('order-id-display');

    trackingForm.addEventListener('submit', function (event) {
        event.preventDefault(); // Evita que la página se recargue

        const orderId = orderInput.value.trim();

        if (orderId) {
            // Si el usuario ingresó un ID, lo mostramos y revelamos los resultados
            orderIdDisplay.textContent = orderId;
            resultsSection.style.display = 'block';

            // Opcional: Desplazar la vista hacia los resultados
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        } else {
            // Si no ingresó nada, oculta los resultados (si estaban visibles)
            resultsSection.style.display = 'none';
            alert('Por favor, ingresa un número de pedido.');
        }
    });
});