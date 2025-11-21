document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('faq-search-input');
    const resultsContainer = document.getElementById('faq-results-list');
    const noResultsMessage = document.getElementById('no-results-message');
    
    
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

    
    function normalizeText(text) {
        return text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
    }

    
    function performSearch() {
        const searchTerm = normalizeText(searchInput.value);
        
        
        resultsContainer.innerHTML = '';

        if (searchTerm.length < 3) {
            
            resultsContainer.classList.remove('active');
            noResultsMessage.style.display = 'none';
            return;
        }

        let visibleCount = 0;
        
        
        knowledgeBase.forEach(item => {
            const questionText = normalizeText(item.q);
            const answerText = normalizeText(item.a); 

            if (questionText.includes(searchTerm) || answerText.includes(searchTerm)) {
                
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

        
        if (visibleCount > 0) {
            resultsContainer.classList.add('active'); 
            noResultsMessage.style.display = 'none';
        } else {
            resultsContainer.classList.remove('active'); 
            noResultsMessage.style.display = 'block';
        }
    }

    
    searchInput.addEventListener('input', performSearch);
    
    
    
    resultsContainer.addEventListener('click', function(event) {
        const questionButton = event.target.closest('.faq-question');
        
        if (!questionButton) return; 

        const answer = questionButton.nextElementSibling;
        
        
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
