// Элементы DOM
const sessionSelect = document.getElementById("session-select");
const userSelect = document.getElementById("user-select");

// Заблокируем выбор пользователя, если сессия не выбрана
if (!sessionSelect.value) {
    userSelect.disabled = true;
}

// Обработчик изменения сессии
sessionSelect.addEventListener("change", function () {
    const sessionId = this.value;
    if (sessionId) {
        // Перезагружаем страницу с параметром session_id
        window.location.href = `/all_chats?session_id=${sessionId}`;
    }
});

// Обработчик изменения пользователя
userSelect.addEventListener("change", function () {
    const sessionId = sessionSelect.value;
    const userId = this.value;
    if (sessionId && userId) {
        // Перезагружаем страницу с параметрами session_id и user_id
        window.location.href = `/all_chats?session_id=${sessionId}&user_id=${userId}`;
    }
});

// Функция для загрузки пользователей
function loadUsersForSession(sessionId, selectedUserId) {
    if (sessionId) {
        fetch(`/users_by_session?session_id=${sessionId}`)
            .then((response) => response.json())
            .then((data) => {
                userSelect.disabled = false;
                userSelect.innerHTML =
                    '<option value="" disabled selected>-- Выберите пользователя --</option>';
                data.users.forEach((user) => {
                    const option = document.createElement("option");
                    option.value = user.id;
                    option.textContent = user.full_name || user.username;
                    if (parseInt(user.id) === parseInt(selectedUserId)) {
                        option.selected = true;
                    }
                    userSelect.appendChild(option);
                });
            })
            .catch((error) => {
                console.error("Ошибка загрузки пользователей:", error);
                userSelect.disabled = true;
                userSelect.innerHTML =
                    '<option value="" disabled>-- Ошибка загрузки пользователей --</option>';
            });
    } else {
        userSelect.disabled = true;
        userSelect.innerHTML =
            '<option value="" disabled>-- Выберите пользователя --</option>';
    }
}

// Загружаем пользователей при загрузке страницы
const currentSessionId = sessionSelect.value;
const currentUserId = userSelect.getAttribute("data-selected-user");
if (currentSessionId) {
    loadUsersForSession(currentSessionId, currentUserId);
}
