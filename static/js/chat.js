document.getElementById('send-button').addEventListener('click', sendMessage);
document.getElementById('clear-button').addEventListener('click', clearChat);

document.getElementById('agent-select').addEventListener('change', function() {
    const agentId = this.value;
    if (agentId) {
        // AJAX-запрос для получения данных агента
        fetch(`/get_agent_data/${agentId}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert("Ошибка: агент не найден.");
                    return;
                }

                // Устанавливаем начальные сообщения и статус агента
                document.getElementById('start-message').innerText = data.start_message;
                document.getElementById('error-message').innerText = data.error_message;
                document.getElementById('agent-name').innerText = `Агент: ${data.name}`;
                document.querySelector('.agent-status').innerText = `Агент ${data.is_active ? 'включен' : 'выключен'}`;

                // Показываем контейнер чата и стартовое сообщение
                document.getElementById('agent-message').style.display = 'block';
                document.querySelector('.chat-container').style.display = 'block';

                // Очищаем старые сообщения и добавляем стартовое сообщение в чат
                const chatBox = document.getElementById('chat-box');
                chatBox.innerHTML = ""; // Очистка чата
                const startMessage = document.createElement('div');
                startMessage.classList.add('message', 'bot-message');
                startMessage.innerHTML = `<span>${data.start_message}</span>`;
                chatBox.appendChild(startMessage);
            })
            .catch(error => console.error('Ошибка:', error));
    } else {
        document.getElementById('agent-message').style.display = 'none';
        document.querySelector('.chat-container').style.display = 'none';
    }
});

function sendMessage() {
    const chatInput = document.getElementById('chat-input');
    const messageText = chatInput.value.trim();
    if (messageText === "") return;

    const chatBox = document.getElementById('chat-box');

    // Добавляем сообщение пользователя
    const userMessage = document.createElement('div');
    userMessage.classList.add('message', 'user-message');
    userMessage.textContent = messageText;
    chatBox.appendChild(userMessage);

    // Очищаем поле ввода
    chatInput.value = "";

    // Прокручиваем вниз
    chatBox.scrollTop = chatBox.scrollHeight;

    // Здесь можно добавить логику отправки сообщения на сервер и получения ответа от бота
}

function clearChat() {
    const chatBox = document.getElementById('chat-box');
    chatBox.innerHTML = "";
}
