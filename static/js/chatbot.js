
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
                    <i class='bx bx-message-dots chat-icon'></i>
                    <i class='bx bx-x close-icon'></i>
                </button>

                <div class="chatbot-window" id="chatbot-window">
                    <div class="chatbot-header">
                        <div class="chatbot-avatar">
                            <i class='bx bx-bot'></i>
                        </div>
                        <div class="chatbot-header-info">
                            <h3>Asistente TechTop</h3>
                            <p>En línea ahora</p>
                        </div>
                        <button type="button" class="header-close-btn" onclick="chatbot.toggleChat()">
                            <i class='bx bx-x'></i>
                        </button>
                    </div>

                    <div class="chatbot-messages" id="chatbot-messages">
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
                            <i class='bx bxs-send'></i>
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
            '🔥 Ofertas',
            '📦 Rastrear pedido',
            '🚚 Tiempos de envío',
            '💳 Medios de pago',
            '🛡️ Garantías',
            '📞 Contacto',
            '❓ Centro de Ayuda'
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
        
        const quickRepliesElement = document.querySelector('.quick-replies');
        if (quickRepliesElement) {
            quickRepliesElement.remove();
        }

        
        const input = document.getElementById('chatbot-input');
        
        const cleanReply = reply.replace(/[🔍📦💳📞🔥🚚🛡️❓]/g, '').trim();
        input.value = cleanReply;
        this.sendMessage();
    }

    async sendMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input.value.trim();

        if (!message) return;

        
        this.addMessage({
            type: 'user',
            text: message,
            timestamp: new Date()
        });

        input.value = '';
        
        
        this.showTypingIndicator();

        try {
            
            const response = await this.sendToBackend(message);
            
            
            this.removeTypingIndicator();

            
            this.addMessage({
                type: 'bot',
                text: response.message,
                timestamp: new Date(),
                data: response.data
            });
            
            
            
            this.showQuickReplies();

        } catch (error) {
            console.error('Error sending message:', error);
            this.removeTypingIndicator();
            this.addMessage({
                type: 'bot',
                text: 'Lo siento, hubo un error al procesar tu mensaje. Por favor, intenta de nuevo.',
                timestamp: new Date()
            });
            
            
            
            this.showQuickReplies();
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


let chatbot;
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        chatbot = new TechTopChatbot();
    });
} else {
    chatbot = new TechTopChatbot();
}
