document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const newChatBtn = document.getElementById('new-chat-btn');
    const chatHistory = document.getElementById('chat-history');

    // Add an event listener for the "New Chat" button
    newChatBtn.addEventListener('click', function() {
        chatHistory.innerHTML = ''; // Clear chat history on the client side
        console.log('New chat started.'); // Optional: Log new chat start
    });

    // Add an event listener for the chat form submission
    chatForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent traditional form submission
        const userInput = document.getElementById('user-input').value.trim();

        if (userInput !== '') {
            addMessage('user', userInput); // Add user's message to chat

            // Send POST request to the backend using Fetch API
            fetch('http://127.0.0.1:8000/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken') // Include CSRF token for security
                },
                body: JSON.stringify({ message: userInput })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                addMessage('bot', data.message); // Add bot's message
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage('bot', 'Sorry, there was an error processing your request.'); // Error message
            });

            document.getElementById('user-input').value = ''; // Clear input field
        }
    });

    // Function to add chat messages dynamically to the chat history
    function addMessage(sender, text, isHTML = false) {
        const message = document.createElement('div');
        message.classList.add('message', sender);

        // Create avatar for the message
        const avatar = document.createElement('div');
        avatar.classList.add('avatar', sender === 'user' ? 'user-avatar' : 'bot-avatar');
        message.appendChild(avatar);

        // Create text container for the message
        const messageText = document.createElement('div');
        messageText.classList.add('text');

        // Set text based on whether it's HTML or plain text
        if (isHTML) {
            messageText.innerHTML = text; // Set as HTML
        } else {
            messageText.textContent = text; // Set as plain text
        }

        message.appendChild(messageText);
        chatHistory.appendChild(message);

        // Scroll to the bottom of the chat history
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // Function to get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Check if the cookie name matches the requested name
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Password visibility toggle
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');

    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', function() {
            // Toggle the type attribute
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);

            // Toggle the eye icon
            this.textContent = type === 'password' ? '👁️' : '🚫';
        });

        // Add a focus event to show the icon when the user focuses on the password input
        passwordInput.addEventListener('focus', function() {
            togglePassword.style.display = 'inline'; // Show the toggle icon when focused
        });

        // Hide the toggle icon when the user leaves the password input
        passwordInput.addEventListener('blur', function() {
            togglePassword.style.display = 'none'; // Hide the toggle icon when not focused
        });
    }
});
