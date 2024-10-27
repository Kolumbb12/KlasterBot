document.getElementById('send-button').addEventListener('click', sendMessage);
document.getElementById('clear-button').addEventListener('click', clearChat);

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

    // Здесь вы можете добавить логику для отправки сообщения на сервер
    // и получения ответа от бота
}

function clearChat() {
    const chatBox = document.getElementById('chat-box');
    chatBox.innerHTML = "";
}