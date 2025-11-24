document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('faq-search-input');
    const resultsContainer = document.getElementById('faq-results-list');
    const noResultsMessage = document.getElementById('no-results-message');
    
    // 1. Cargar la base de conocimiento desde la etiqueta <script>
    let knowledgeBase = [];
    try {
        const dbElement = document.getElementById('faq-database');
        if (dbElement) {
            knowledgeBase = JSON.parse(dbElement.textContent);
        } else {
            console.error("Error: No se encontró la base de conocimiento #faq-database");
        }
    } catch (e) {
        console.error("Error al parsear la base de conocimiento JSON:", e);
    }

    // 2. Función para normalizar texto (quitar tildes, etc.)
    function normalizeText(text) {
        return text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
    }

    // 3. Función de búsqueda
    function performSearch() {
        const searchTerm = normalizeText(searchInput.value);
        
        // Limpiar resultados anteriores
        resultsContainer.innerHTML = '';

        if (searchTerm.length < 3) {
            // No buscar si es muy corto, y ocultar todo
            resultsContainer.classList.remove('active');
            noResultsMessage.style.display = 'none';
            return;
        }

        let visibleCount = 0;
        
        // Filtrar la base de conocimiento
        knowledgeBase.forEach(item => {
            const questionText = normalizeText(item.q);
            const answerText = normalizeText(item.a); // También busca en la respuesta

            if (questionText.includes(searchTerm) || answerText.includes(searchTerm)) {
                // Si hay coincidencia, crear el elemento HTML
                const faqItem = document.createElement('div');
                faqItem.className = 'faq-item';
                faqItem.innerHTML = `
                    <button class="faq-question">
                        <span>${item.q}</span>
                        <i class='bx bx-plus'></i>
                    </button>
                    <div class="faq-answer">
                        ${item.a}
                    </div>
                `;
                resultsContainer.appendChild(faqItem);
                visibleCount++;
            }
        });

        // 4. Mostrar/ocultar "No encontrado" o la lista de resultados
        if (visibleCount > 0) {
            resultsContainer.classList.add('active'); // Muestra el contenedor de resultados
            noResultsMessage.style.display = 'none';
        } else {
            resultsContainer.classList.remove('active'); // Oculta el contenedor si no hay nada
            noResultsMessage.style.display = 'block';
        }
    }

    // 5. Escuchar el evento 'input' (mientras el usuario escribe)
    searchInput.addEventListener('input', performSearch);
    
    // 6. Funcionalidad de Acordeón (usando delegación de eventos)
    // Esto funciona incluso para los elementos creados dinámicamente
    resultsContainer.addEventListener('click', function(event) {
        const questionButton = event.target.closest('.faq-question');
        
        if (!questionButton) return; // No se hizo clic en un botón

        const answer = questionButton.nextElementSibling;
        
        // Alternar 'active' y la altura de la respuesta
        questionButton.classList.toggle('active');
        if (answer.style.maxHeight) {
            answer.style.maxHeight = null;
            answer.style.paddingTop = null;
        } else {
            answer.style.paddingTop = '10px';
            answer.style.maxHeight = answer.scrollHeight + 30 + 'px';
        }
    });
});