/*
chat.js
Этот файл содержит JavaScript-код для управления взаимодействием на странице чата.
Основные функции включают отправку сообщений, очистку истории чата, загрузку истории чата и переключение агентов.

Основные компоненты:
1. `toggleAgentStatus(agentId)`: Изменяет статус агента.
2. `loadChatHistory(agentId, startMessageText)`: Загружает историю чата для выбранного агента и добавляет стартовое
сообщение, если история пуста.
3. `sendMessage()`: Отправляет сообщение пользователя и отображает ответ агента в чате.
4. `clearChat()`: Очищает историю чата для выбранного агента.
5. Обработчики событий: Отвечают за нажатие клавиш и выбор агента, обновляя историю чата и интерфейс пользователя.
*/

// Обработчик события для кнопки отправки сообщения
document.getElementById('send-button').addEventListener('click', sendMessage);
// Обработчик события для кнопки очистки чата
document.getElementById('clear-button').addEventListener('click', clearChat);

// Обработчик выбора агента
document.getElementById('agent-select').addEventListener('change', function() {
    const agentId = this.value;
    if (agentId) {
        // Обновляем URL с параметром agent_id при выборе нового агента
        window.history.pushState({}, '', `/chat?agent_id=${agentId}`);

        fetch(`/get_agent_data/${agentId}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert("Ошибка: агент не найден.");
                    return;
                }

                // Обновление информации об агенте
                document.getElementById('start-message').innerText = data.start_message;
                document.getElementById('error-message').innerText = data.error_message;
                document.getElementById('agent-name').innerText = `Агент: ${data.name}`;
                document.querySelector('.agent-status').innerText = `Агент ${data.is_active ? 'включен' : 'выключен'}`;

                document.getElementById('agent-message').style.display = 'block';
                document.querySelector('.chat-container').style.display = 'block';

                // Загружаем историю чата после стартового сообщения
                loadChatHistory(agentId, data.start_message);
            })
            .catch(error => console.error('Ошибка:', error));
    } else {
        document.getElementById('agent-message').style.display = 'none';
        document.querySelector('.chat-container').style.display = 'none';
    }
});

// Функция для загрузки истории чата
function loadChatHistory(agentId, startMessageText) {
    // AJAX-запрос для получения истории чата
    fetch(`/chat_history?agent_id=${agentId}`)
        .then(response => response.json())
        .then(data => {
            const chatBox = document.getElementById('chat-box');
            chatBox.innerHTML = ''; // Очищаем окно чата

            // Добавляем стартовое сообщение только если история пуста
            const startMessageDiv = document.createElement('div');
            startMessageDiv.classList.add('message', 'bot-message', 'start-message');
            startMessageDiv.innerHTML = `<span>${startMessageText}</span>`;
            chatBox.appendChild(startMessageDiv);

            // Отображение истории сообщений
            data.chat_history.forEach(message => {
                const messageDiv = document.createElement('div');
                messageDiv.classList.add('message', message.role === 'user' ? 'user-message' : 'bot-message');
                messageDiv.textContent = message.content;
                chatBox.appendChild(messageDiv);
            });
            // Прокрутка чата вниз
            chatBox.scrollTop = chatBox.scrollHeight;
        })
        .catch(error => console.error('Ошибка при загрузке истории чата:', error));
}

// Функция для отправки сообщения
function sendMessage() {
    const agentId = document.getElementById('agent-select').value;
    const chatInput = document.getElementById('chat-input');
    const messageText = chatInput.value.trim();

    if (!agentId || messageText === "") return;

    const chatBox = document.getElementById('chat-box');
    const userMessage = document.createElement('div');
    userMessage.classList.add('message', 'user-message');
    userMessage.textContent = messageText;
    chatBox.appendChild(userMessage);

    // Анимация появления сообщения пользователя
    userMessage.style.opacity = '0';
    setTimeout(() => {
        userMessage.style.transition = "opacity 0.5s";
        userMessage.style.opacity = '1';
    }, 100);

    chatInput.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    // Отправка сообщения на сервер
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ agent_id: agentId, chat_type_id: 1, message: messageText })  // Передаем chat_type_id
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error(data.error);
            alert("Ошибка: " + data.error);
        } else {
            const botMessage = document.createElement('div');
            botMessage.classList.add('message', 'bot-message');
            botMessage.textContent = data.response;
            chatBox.appendChild(botMessage);

            // Анимация появления сообщения бота
            botMessage.style.opacity = '0';
            setTimeout(() => {
                botMessage.style.transition = "opacity 0.5s";
                botMessage.style.opacity = '1';
            }, 100);

            chatBox.scrollTop = chatBox.scrollHeight;
        }
    })
    .catch(error => console.error('Ошибка:', error));
}

// Функция для очистки чата
function clearChat() {
    const agentId = document.getElementById('agent-select').value;
    if (!agentId) {
        alert("Пожалуйста, выберите агента перед очисткой чата.");
        return;
    }

    fetch('/clear_chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ agent_id: agentId, chat_type_id: 1 }) // Задаем тип чата (1 - для тестового)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error(data.error);
            alert("Ошибка: " + data.error);
        } else {
            // Очищаем окно чата после успешного удаления
            const chatBox = document.getElementById('chat-box');
            chatBox.innerHTML = '';
            alert(data.success);
        }
    })
    .catch(error => console.error('Ошибка:', error));
}

// Получаем элементы ввода и кнопки
const chatInput = document.getElementById('chat-input');
const sendButton = document.getElementById('send-button');

// Добавляем обработчик события на нажатие Enter в поле ввода
chatInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
        event.preventDefault(); // Предотвращаем стандартное поведение Enter (новая строка)
        sendButton.click(); // Программно нажимаем кнопку отправки
    }
});

// Загрузка истории чата при загрузке страницы с выбранным агентом по умолчанию
window.addEventListener('load', () => {
    const agentId = document.getElementById('agent-select').value;
    if (agentId) {
        loadChatHistory(agentId);
    }
});
