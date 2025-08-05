// Chat Interface JavaScript
(function() {
    const vscode = acquireVsCodeApi();
    
    // DOM elements
    const chatMessages = document.getElementById('chatMessages');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const clearBtn = document.getElementById('clearBtn');
    const typingIndicator = document.getElementById('typingIndicator');
    const charCount = document.getElementById('charCount');
    
    // State
    let isWaitingForResponse = false;
    
    // Initialize
    document.addEventListener('DOMContentLoaded', function() {
        setupEventListeners();
        adjustTextareaHeight();
        vscode.postMessage({ type: 'ready' });
    });
    
    function setupEventListeners() {
        // Send button click
        sendBtn.addEventListener('click', sendMessage);
        
        // Clear button click
        clearBtn.addEventListener('click', clearChat);
        
        // Input handling
        chatInput.addEventListener('input', function() {
            adjustTextareaHeight();
            updateCharCount();
            updateSendButton();
        });
        
        // Enter key handling
        chatInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    sendMessage();
                } else if (!e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            }
        });
        
        // Paste handling
        chatInput.addEventListener('paste', function(e) {
            setTimeout(() => {
                adjustTextareaHeight();
                updateCharCount();
                updateSendButton();
            }, 0);
        });
    }
    
    function sendMessage() {
        const message = chatInput.value.trim();
        if (!message || isWaitingForResponse) return;
        
        // Send message to extension
        vscode.postMessage({
            type: 'sendMessage',
            text: message
        });
        
        // Clear input
        chatInput.value = '';
        adjustTextareaHeight();
        updateCharCount();
        updateSendButton();
        
        // Set waiting state
        isWaitingForResponse = true;
        sendBtn.disabled = true;
    }
    
    function clearChat() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            vscode.postMessage({ type: 'clearHistory' });
        }
    }
    
    function adjustTextareaHeight() {
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
    }
    
    function updateCharCount() {
        const count = chatInput.value.length;
        charCount.textContent = `${count}/2000`;
        
        if (count > 1800) {
            charCount.style.color = 'var(--vscode-errorForeground)';
        } else if (count > 1500) {
            charCount.style.color = 'var(--vscode-warningForeground)';
        } else {
            charCount.style.color = 'var(--vscode-descriptionForeground)';
        }
    }
    
    function updateSendButton() {
        const hasText = chatInput.value.trim().length > 0;
        const isNotTooLong = chatInput.value.length <= 2000;
        sendBtn.disabled = !hasText || !isNotTooLong || isWaitingForResponse;
    }
    
    function addMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Process message content for markdown-like formatting
        let processedContent = message.content;
        
        // Convert code blocks
        processedContent = processedContent.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
            return `<pre><code class="language-${lang || ''}">${escapeHtml(code.trim())}</code></pre>`;
        });
        
        // Convert inline code
        processedContent = processedContent.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Convert line breaks
        processedContent = processedContent.replace(/\n/g, '<br>');
        
        contentDiv.innerHTML = processedContent;
        
        const timestampDiv = document.createElement('div');
        timestampDiv.className = 'message-timestamp';
        timestampDiv.textContent = formatTimestamp(message.timestamp || Date.now());
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timestampDiv);
        
        // Remove welcome message if this is the first real message
        const welcomeMessage = chatMessages.querySelector('.welcome-message');
        if (welcomeMessage && chatMessages.children.length > 1) {
            welcomeMessage.remove();
        }
        
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }
    
    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = `❌ ${message}`;
        
        chatMessages.appendChild(errorDiv);
        scrollToBottom();
        
        // Remove error after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 5000);
    }
    
    function showTyping(isTyping) {
        if (isTyping) {
            typingIndicator.style.display = 'flex';
        } else {
            typingIndicator.style.display = 'none';
        }
        scrollToBottom();
    }
    
    function clearChatHistory() {
        // Remove all messages except welcome message
        const messages = chatMessages.querySelectorAll('.message:not(.welcome-message .message)');
        messages.forEach(msg => msg.remove());
        
        // Remove error messages
        const errors = chatMessages.querySelectorAll('.error-message');
        errors.forEach(error => error.remove());
        
        // Show welcome message if it was removed
        if (!chatMessages.querySelector('.welcome-message')) {
            location.reload();
        }
    }
    
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Handle messages from the extension
    window.addEventListener('message', event => {
        const message = event.data;
        
        switch (message.type) {
            case 'userMessage':
                addMessage(message.message, true);
                break;
                
            case 'assistantMessage':
                addMessage(message.message, false);
                isWaitingForResponse = false;
                sendBtn.disabled = false;
                updateSendButton();
                break;
                
            case 'typing':
                showTyping(message.isTyping);
                break;
                
            case 'error':
                showError(message.message);
                isWaitingForResponse = false;
                sendBtn.disabled = false;
                updateSendButton();
                showTyping(false);
                break;
                
            case 'clearHistory':
                clearChatHistory();
                break;
                
            case 'ready':
                console.log('Chat interface ready:', message.message);
                break;
        }
    });
    
    // Focus input on load
    setTimeout(() => {
        chatInput.focus();
    }, 100);
})();