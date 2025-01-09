

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

function toggleSetupMode() {
    const platformSelect = document.getElementById('platform');
    const setupOptions = document.getElementById('setup-options');

    if (platformSelect.value === "2") { // ID Telegram (bot)
        setupOptions.style.display = "block";
    } else {
        setupOptions.style.display = "none";
        document.getElementById('manual-setup').style.display = "none";
        document.getElementById('auto-setup').style.display = "none";
    }
}

function toggleFields() {
    const setupMode = document.getElementById('setup_mode').value;
    document.getElementById('manual-setup').style.display = setupMode === "manual" ? "block" : "none";
    document.getElementById('auto-setup').style.display = setupMode === "auto" ? "block" : "none";
}