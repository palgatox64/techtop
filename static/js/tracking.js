document.addEventListener('DOMContentLoaded', function () {
    const trackingForm = document.getElementById('tracking-form');
    const resultsSection = document.getElementById('results-section');
    const orderInput = document.getElementById('order-input');
    const orderIdDisplay = document.getElementById('order-id-display');

    trackingForm.addEventListener('submit', function (event) {
        event.preventDefault(); 

        const orderId = orderInput.value.trim();

        if (orderId) {
            
            orderIdDisplay.textContent = orderId;
            resultsSection.style.display = 'block';

            
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        } else {
            
            resultsSection.style.display = 'none';
            alert('Por favor, ingresa un número de pedido.');
        }
    });
});
