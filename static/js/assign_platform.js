function toggleTokenField() {
    const platformSelect = document.getElementById('platform');
    const tokenField = document.getElementById('token-field');

    // Показываем поле токена только для Telegram (bot), ID = 2
    if (platformSelect.value === "2") {
        tokenField.style.display = "block";
    } else {
        tokenField.style.display = "none";
        document.getElementById('api_token').value = ""; // Очистка поля токена
        hideErrorMessage();
    }
}

function validateForm() {
    const platformSelect = document.getElementById('platform');
    const tokenInput = document.getElementById('api_token');
    const errorMessage = document.getElementById('error-message');

    // Проверяем только для Telegram (bot)
    if (platformSelect.value === "2") {
        const token = tokenInput.value.trim();

        // Регулярное выражение для проверки токена Telegram
        const tokenRegex = /^\d{8,10}:[A-Za-z0-9_-]{35,}$/;
        if (!tokenRegex.test(token)) {
            errorMessage.style.display = "block";
            return false; // Отменяем отправку формы
        }
    }

    hideErrorMessage();
    return true; // Разрешаем отправку формы
}

function hideErrorMessage() {
    const errorMessage = document.getElementById('error-message');
    errorMessage.style.display = "none";
}