// JavaScript for real-time messaging functionality

document.addEventListener('DOMContentLoaded', function() {
    const messagesList = document.getElementById('messages-list');
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const conversationId = messagesList ? messagesList.getAttribute('data-conversation-id') : null;
    const senderId = messagesList ? messagesList.getAttribute('data-sender-id') : null;
    
    let chatSocket = null;
    
    // Initialize WebSocket for messaging if on conversation page
    if (conversationId && senderId) {
        // Connect to WebSocket
        chatSocket = new WebSocket(
            'ws://' + window.location.host + '/ws/chat/' + conversationId + '/'
        );
        
        // WebSocket event handlers
        chatSocket.onopen = function(e) {
            console.log('WebSocket connection established');
        };
        
        chatSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            addMessageToChat(data.message, data.sender_id, data.created_at, data.message_id);
            
            // Scroll to bottom of messages list
            messagesList.scrollTop = messagesList.scrollHeight;
        };
        
        chatSocket.onclose = function(e) {
            console.log('WebSocket connection closed');
        };
        
        // Form submission handler
        if (messageForm) {
            messageForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const message = messageInput.value.trim();
                if (message === '') return;
                
                // Send message via WebSocket
                chatSocket.send(JSON.stringify({
                    'message': message,
                    'sender_id': senderId
                }));
                
                // Clear input field
                messageInput.value = '';
            });
        }
        
        // Scroll to bottom of messages list when page loads
        if (messagesList) {
            messagesList.scrollTop = messagesList.scrollHeight;
        }
    }
    
    // Function to add a message to the chat
    function addMessageToChat(message, messageSenderId, timestamp, messageId) {
        const isCurrentUser = messageSenderId === senderId;
        const messageClass = isCurrentUser ? 'sent' : 'received';
        
        const formattedTime = formatTimestamp(timestamp);
        
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', messageClass);
        messageElement.setAttribute('data-message-id', messageId);
        
        messageElement.innerHTML = `
            <div class="message-content">${escapeHtml(message)}</div>
            <div class="message-time">${formattedTime}</div>
        `;
        
        messagesList.appendChild(messageElement);
        
        // If message is received (not sent by current user), mark as read
        if (!isCurrentUser) {
            markMessageAsRead(messageId);
        }
    }
    
    // Function to mark message as read via AJAX
    function markMessageAsRead(messageId) {
        fetch(`/messages/api/mark-read/${messageId}/`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        }).catch(error => {
            console.error('Error marking message as read:', error);
        });
    }
    
    // Format timestamp for display
    function formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        let hours = date.getHours();
        const minutes = date.getMinutes();
        const ampm = hours >= 12 ? 'PM' : 'AM';
        
        hours = hours % 12;
        hours = hours ? hours : 12; // the hour '0' should be '12'
        const formattedMinutes = minutes < 10 ? '0' + minutes : minutes;
        
        return `${hours}:${formattedMinutes} ${ampm}`;
    }
    
    // Helper function to escape HTML content
    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
    
    // Unread message count updater for inbox
    const unreadCounters = document.querySelectorAll('.unread-count');
    if (unreadCounters.length > 0) {
        // Check for new messages every minute
        setInterval(function() {
            fetch('/messages/inbox/', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                data.conversations.forEach(conversation => {
                    const counter = document.querySelector(`.unread-count[data-conversation-id="${conversation.id}"]`);
                    if (counter) {
                        counter.textContent = conversation.unread_count;
                        if (conversation.unread_count > 0) {
                            counter.classList.remove('d-none');
                        } else {
                            counter.classList.add('d-none');
                        }
                    }
                });
            })
            .catch(error => {
                console.error('Error fetching unread counts:', error);
            });
        }, 60000); // Check every minute
    }
});
