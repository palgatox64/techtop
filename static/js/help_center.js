document.addEventListener('DOMContentLoaded', function () {
    const faqQuestions = document.querySelectorAll('.faq-question');

    faqQuestions.forEach(button => {
        button.addEventListener('click', () => {
            const answer = button.nextElementSibling;
            
            // Alternar la clase 'active' en el botón
            button.classList.toggle('active');

            // Alternar la altura del panel de respuesta
            if (answer.style.maxHeight) {
                answer.style.maxHeight = null;
                answer.style.paddingTop = null;
            } else {
                // Añade padding para una transición más suave
                answer.style.paddingTop = '10px';
                answer.style.maxHeight = answer.scrollHeight + 30 + 'px';
            }
        });
    });
});