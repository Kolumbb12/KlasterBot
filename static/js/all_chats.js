/*
all_chats.js
Этот файл содержит JavaScript-код для управления отображением чатов на странице.
Включает функции для управления выбором сессии, загрузкой пользователей и обновлением истории чатов.

Основные компоненты:
1. Обработчики событий для выбора сессии и пользователя.
2. Функция `loadUsersForSession()` для загрузки списка пользователей для выбранной сессии.
3. Инициализация текущих данных при загрузке страницы.
*/

// Элементы DOM
const sessionSelect = document.getElementById("session-select"); // Выпадающий список сессий
const userSelect = document.getElementById("user-select"); // Выпадающий список пользователей

// Заблокируем выбор пользователя, если сессия не выбрана
if (!sessionSelect.value) {
    userSelect.disabled = true;
}

// Обработчик изменения сессии
sessionSelect.addEventListener("change", function () {
    const sessionId = this.value; // Получаем выбранный session_id
    if (sessionId) {
        // Перезагружаем страницу с параметром session_id
        window.location.href = `/all_chats?session_id=${sessionId}`;
    }
});

// Обработчик изменения пользователя
userSelect.addEventListener("change", function () {
    const sessionId = sessionSelect.value; // Получаем session_id
    const userId = this.value; // Получаем user_id
    if (sessionId && userId) {
        // Перезагружаем страницу с параметрами session_id и user_id
        window.location.href = `/all_chats?session_id=${sessionId}&user_id=${userId}`;
    }
});

// Функция для загрузки пользователей
function loadUsersForSession(sessionId, selectedUserId) {
    if (sessionId) {
        fetch(`/users_by_session?session_id=${sessionId}`) // Выполняем запрос для получения списка пользователей
            .then((response) => response.json())
            .then((data) => {
                userSelect.disabled = false; // Разблокируем выбор пользователя
                userSelect.innerHTML =
                    '<option value="" disabled selected>-- Выберите пользователя --</option>'; // Обновляем выпадающий список
                data.users.forEach((user) => {
                    const option = document.createElement("option");
                    option.value = user.id; // Устанавливаем user_id в качестве значения
                    option.textContent = user.full_name || user.username; // Отображаем имя или логин пользователя
                    if (parseInt(user.id) === parseInt(selectedUserId)) {
                        option.selected = true; // Выбираем текущего пользователя
                    }
                    userSelect.appendChild(option);
                });
            })
            .catch((error) => {
                console.error("Ошибка загрузки пользователей:", error); // Логируем ошибки
                userSelect.disabled = true; // Блокируем выбор пользователя в случае ошибки
                userSelect.innerHTML =
                    '<option value="" disabled>-- Ошибка загрузки пользователей --</option>';
            });
    } else {
        userSelect.disabled = true; // Блокируем выбор, если сессия не выбрана
        userSelect.innerHTML =
            '<option value="" disabled>-- Выберите пользователя --</option>';
    }
}

// Загружаем пользователей при загрузке страницы
const currentSessionId = sessionSelect.value; // Текущий session_id
const currentUserId = userSelect.getAttribute("data-selected-user"); // Текущий user_id
if (currentSessionId) {
    loadUsersForSession(currentSessionId, currentUserId); // Загружаем список пользователей для выбранной сессии
}
