// Chatbot functionality
class TechTopChatbot {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.init();
    }

    init() {
        this.createChatbotHTML();
        this.attachEventListeners();
        this.showWelcomeMessage();
    }

    createChatbotHTML() {
        const chatbotHTML = `
            <div class="chatbot-container">
                <button class="chatbot-button" id="chatbot-toggle">
                    <svg class="chat-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                        <path d="M12 2C6.48 2 2 6.48 2 12c0 1.54.36 2.98.97 4.29L1 22l5.71-1.97C8.02 21.64 9.46 22 11 22h1c5.52 0 10-4.48 10-10S17.52 2 12 2zm0 18c-1.38 0-2.63-.36-3.73-1L6 20l1-2.27C6.36 16.63 6 15.38 6 14c0-4.41 3.59-8 8-8s8 3.59 8 8-3.59 8-8 8z"/>
                        <circle cx="9" cy="13" r="1.5"/>
                        <circle cx="15" cy="13" r="1.5"/>
                        <path d="M9 10h1v2H9zm5 0h1v2h-1z"/>
                    </svg>
                    <span class="chatbot-button-text">TechTop Assistant</span>
                    <svg class="close-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                    </svg>
                </button>

                <div class="chatbot-window" id="chatbot-window">
                    <div class="chatbot-header">
                        <div class="chatbot-avatar">🤖</div>
                        <div class="chatbot-header-info">
                            <h3>TechTop Assistant</h3>
                            <p>Siempre en línea • Respuesta rápida</p>
                        </div>
                    </div>

                    <div class="chatbot-messages" id="chatbot-messages">
                        <!-- Messages will be inserted here -->
                    </div>

                    <div class="chatbot-input-container">
                        <input 
                            type="text" 
                            class="chatbot-input" 
                            id="chatbot-input" 
                            placeholder="Escribe tu mensaje..."
                            autocomplete="off"
                        >
                        <button class="chatbot-send-btn" id="chatbot-send">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', chatbotHTML);
    }

    attachEventListeners() {
        const toggleBtn = document.getElementById('chatbot-toggle');
        const sendBtn = document.getElementById('chatbot-send');
        const input = document.getElementById('chatbot-input');

        toggleBtn.addEventListener('click', () => this.toggleChat());
        sendBtn.addEventListener('click', () => this.sendMessage());
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
    }

    toggleChat() {
        this.isOpen = !this.isOpen;
        const chatWindow = document.getElementById('chatbot-window');
        const toggleBtn = document.getElementById('chatbot-toggle');

        if (this.isOpen) {
            chatWindow.classList.add('active');
            toggleBtn.classList.add('active');
            document.getElementById('chatbot-input').focus();
        } else {
            chatWindow.classList.remove('active');
            toggleBtn.classList.remove('active');
        }
    }

    showWelcomeMessage() {
        const welcomeMsg = {
            type: 'bot',
            text: `<div class="welcome-message">
                <h4>👋 ¡Hola! Bienvenido a TechTop</h4>
                <p>Soy tu asistente virtual. Puedo ayudarte con:</p>
                <ul style="margin: 8px 0 0 0; padding-left: 20px; font-size: 13px; color: #4a5568;">
                    <li>Información sobre productos</li>
                    <li>Búsqueda de artículos</li>
                    <li>Seguimiento de pedidos</li>
                    <li>Preguntas frecuentes</li>
                </ul>
            </div>`,
            timestamp: new Date()
        };

        this.addMessage(welcomeMsg);
        this.showQuickReplies();
    }

    showQuickReplies() {
        const quickReplies = [
            '🔍 Ver productos',
            '📦 Rastrear pedido',
            '💳 Métodos de pago',
            '📞 Contacto'
        ];

        const repliesHTML = `
            <div class="quick-replies">
                ${quickReplies.map(reply => 
                    `<button class="quick-reply-btn" onclick="chatbot.handleQuickReply('${reply}')">${reply}</button>`
                ).join('')}
            </div>
        `;

        const messagesContainer = document.getElementById('chatbot-messages');
        messagesContainer.insertAdjacentHTML('beforeend', repliesHTML);
        this.scrollToBottom();
    }

    handleQuickReply(reply) {
        // Remove quick replies
        const quickRepliesElement = document.querySelector('.quick-replies');
        if (quickRepliesElement) {
            quickRepliesElement.remove();
        }

        // Send the quick reply as a message
        const input = document.getElementById('chatbot-input');
        const cleanReply = reply.replace(/[🔍📦💳📞]/g, '').trim();
        input.value = cleanReply;
        this.sendMessage();
    }

    async sendMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input.value.trim();

        if (!message) return;

        // Add user message
        this.addMessage({
            type: 'user',
            text: message,
            timestamp: new Date()
        });

        input.value = '';
        
        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send message to backend
            const response = await this.sendToBackend(message);
            
            // Remove typing indicator
            this.removeTypingIndicator();

            // Add bot response
            this.addMessage({
                type: 'bot',
                text: response.message,
                timestamp: new Date(),
                data: response.data
            });

        } catch (error) {
            console.error('Error sending message:', error);
            this.removeTypingIndicator();
            this.addMessage({
                type: 'bot',
                text: 'Lo siento, hubo un error al procesar tu mensaje. Por favor, intenta de nuevo.',
                timestamp: new Date()
            });
        }
    }

    async sendToBackend(message) {
        const csrfToken = this.getCookie('csrftoken');
        
        const response = await fetch('/chatbot/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Server error:', errorText);
            throw new Error(`Server error: ${response.status}`);
        }

        return await response.json();
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    addMessage(message) {
        const messagesContainer = document.getElementById('chatbot-messages');
        const messageHTML = this.createMessageHTML(message);
        messagesContainer.insertAdjacentHTML('beforeend', messageHTML);
        this.scrollToBottom();
    }

    createMessageHTML(message) {
        const time = this.formatTime(message.timestamp);
        const isUser = message.type === 'user';
        
        return `
            <div class="message ${message.type}">
                <div class="message-avatar">${isUser ? '👤' : '🤖'}</div>
                <div>
                    <div class="message-content">
                        <p>${message.text}</p>
                    </div>
                    <div class="message-time">${time}</div>
                </div>
            </div>
        `;
    }

    showTypingIndicator() {
        const messagesContainer = document.getElementById('chatbot-messages');
        const typingHTML = `
            <div class="message bot typing-message">
                <div class="message-avatar">🤖</div>
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        messagesContainer.insertAdjacentHTML('beforeend', typingHTML);
        this.scrollToBottom();
    }

    removeTypingIndicator() {
        const typingMessage = document.querySelector('.typing-message');
        if (typingMessage) {
            typingMessage.remove();
        }
    }

    formatTime(date) {
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chatbot-messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

// Initialize chatbot when DOM is ready
let chatbot;
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        chatbot = new TechTopChatbot();
    });
} else {
    chatbot = new TechTopChatbot();
}
