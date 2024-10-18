document.addEventListener('DOMContentLoaded', function () {
    let conversationId = generateUUID(); // Initialize with a new conversation ID
    const chatForm = document.getElementById('chat-form');
    const newChatBtn = document.getElementById('new-chat-btn');
    const chatHistory = document.getElementById('chat-history');
    const recentConversations = document.getElementById('recent-conversations'); // Container for recent chats

    // Fetch and display recent conversations on page load
    fetchRecentConversations();
    addInitialMessage();

    // Handle chat form submission
    chatForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const userInput = document.getElementById('user-input').value.trim();

        if (userInput !== '') {
            addMessage('user', userInput);
            document.getElementById('user-input').value = ''; // Clear input field

            fetch('/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ message: userInput })
            })
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                addMessage('bot', data.message, true);
                saveChat(userInput, data.message); // Save the conversation
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage('bot', 'Sorry, there was an error processing your request.');
            });

            removeSuggestedQuestions();
        }
    });

    // Save the chat on the server
    function saveChat(userInput, botResponse) {
        fetch('/save_chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                user_question: userInput,
                bot_response: botResponse,
                conversation_id: conversationId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log('Chat saved successfully.');
                fetchRecentConversations(); // Update recent conversations
            } else {
                console.error('Failed to save chat:', data);
            }
        })
        .catch(error => {
            console.error('Error saving chat:', error);
        });
    }

    // Fetch and display recent conversations dynamically
    function fetchRecentConversations() {
        fetch('/fetch_recent_conversations/')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    recentConversations.innerHTML = ''; // Clear old list

                    data.conversations.forEach(convo => {
                        const chatItem = document.createElement('div');
                        chatItem.classList.add('chat-item');
                        chatItem.textContent = convo.title;
                        chatItem.addEventListener('click', function () {
                            // Load the selected conversation
                            conversationId = convo.id;
                            clearChatHistory();
                            fetchChatHistory(conversationId);
                        });
                        recentConversations.appendChild(chatItem);
                    });
                }
            })
            .catch(error => {
                console.error('Error fetching recent conversations:', error);
            });
    }

    // Fetch chat history from the server
    function fetchChatHistory(conversationIdToLoad) {
        fetch(`/fetch_chat_history/?conversation_id=${conversationIdToLoad}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    chatHistory.innerHTML = ''; // Clear existing content
                    data.chat_history.forEach(chat => {
                        addMessage(chat.sender, chat.content, true);
                    });
                } else {
                    console.error('Error fetching chat history:', data.message);
                }
            })
            .catch(error => {
                console.error('Error fetching chat history:', error);
            });
    }

    // Add an initial welcome message with suggested questions
    function addInitialMessage() {
        const initialMessage = document.createElement('div');
        initialMessage.classList.add('message', 'bot');
        initialMessage.innerHTML = `
            <div class="text">
                <p>Welcome to the chatbot! How can I assist you today?</p>
                <div class="suggested-questions">
                    <button class="suggested-question">What is the weather today?</button>
                    <button class="suggested-question">Tell me a joke.</button>
                    <button class="suggested-question">How to make a cake?</button>
                    <button class="suggested-question">What is the capital of France?</button>
                </div>
            </div>
        `;
        chatHistory.appendChild(initialMessage);

        // Add event listeners to suggested question buttons
        initialMessage.querySelectorAll('.suggested-question').forEach(button => {
            button.addEventListener('click', function () {
                const question = this.textContent.trim();
                addMessage('user', question);

                fetch('/chatbot/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({ message: question })
                })
                .then(response => {
                    if (!response.ok) throw new Error('Network response was not ok');
                    return response.json();
                })
                .then(data => {
                    addMessage('bot', data.message, true);
                    saveChat(question, data.message); // Save chat
                })
                .catch(error => {
                    console.error('Error:', error);
                    addMessage('bot', 'Sorry, there was an error processing your request.');
                });

                removeSuggestedQuestions();
            });
        });
    }

    // Add messages to the chat history
    function addMessage(sender, text, isHTML = false) {
        const message = document.createElement('div');
        message.classList.add('message', sender);

        const messageText = document.createElement('div');
        messageText.classList.add('text');

        if (isHTML) {
            messageText.innerHTML = text;
        } else {
            messageText.textContent = text;
        }

        message.appendChild(messageText);
        chatHistory.appendChild(message);
        chatHistory.scrollTop = chatHistory.scrollHeight; // Scroll to bottom
    }

    // Remove suggested questions after they are used
    function removeSuggestedQuestions() {
        const suggestedQuestionsDiv = document.querySelector('.suggested-questions');
        if (suggestedQuestionsDiv) suggestedQuestionsDiv.remove();
    }

    // Generate a UUID for conversation ID
    function generateUUID() {
        // Generate a simple UUID (version 4)
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    // Get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie) {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Add event listener for the "New Chat" button
    newChatBtn.addEventListener('click', function () {
        conversationId = generateUUID(); // Generate a new conversation ID
        clearChatHistory(); // Clear the current chat history
        addInitialMessage(); // Add welcome message
        fetchRecentConversations(); // Refresh recent conversations
    });

    // Clear the chat history on the page
    function clearChatHistory() {
        chatHistory.innerHTML = '';
    }
});
