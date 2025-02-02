document.addEventListener("DOMContentLoaded", function () {
    // Добавляем обработчики событий при загрузке страницы
    document.getElementById('platform').addEventListener('change', toggleSetupMode);
    document.getElementById('setup_mode').addEventListener('change', toggleFields);
    document.querySelector('form').addEventListener('submit', validateForm);
});

// Функция для валидации формы перед отправкой
function validateForm(event) {
    const platformSelect = document.getElementById('platform');
    const tokenInput = document.getElementById('api_token');
    const phoneNumberInput = document.getElementById('phone_number');
    const errorMessage = document.getElementById('error-message');

    // Проверка для Telegram (bot)
    if (platformSelect.value === "2") {
        const token = tokenInput.value.trim();

        // Регулярное выражение для проверки токена Telegram
        const tokenRegex = /^\d{8,10}:[A-Za-z0-9_-]{35,}$/;
        if (!tokenRegex.test(token)) {
            showErrorMessage("Введите корректный токен Telegram!");
            event.preventDefault(); // Отменяем отправку формы
            return false;
        }
    }

    // Проверка для WhatsApp (номер телефона)
    if (platformSelect.value === "4") {
        const phoneNumber = phoneNumberInput.value.trim();

        // Регулярное выражение для проверки номера телефона в международном формате
        const phoneRegex = /^\+\d{11,15}$/;
        if (!phoneRegex.test(phoneNumber)) {
            showErrorMessage("Введите корректный номер телефона в международном формате, например +77012345678.");
            event.preventDefault(); // Отменяем отправку формы
            return false;
        }
    }

    hideErrorMessage();
    return true; // Разрешаем отправку формы
}

// Функция для отображения ошибки
function showErrorMessage(message) {
    const errorMessage = document.getElementById('error-message');
    errorMessage.innerText = message;
    errorMessage.style.display = "block";
}

// Функция для скрытия ошибки
function hideErrorMessage() {
    const errorMessage = document.getElementById('error-message');
    errorMessage.style.display = "none";
}

// Функция для отображения необходимых полей в зависимости от выбранной платформы
function toggleSetupMode() {
    const platformSelect = document.getElementById('platform');
    const setupOptions = document.getElementById('setup-options');
    const manualSetup = document.getElementById('manual-setup');
    const autoSetup = document.getElementById('auto-setup');
    const whatsappSetup = document.getElementById('whatsapp-setup');

    // Скрываем все блоки
    setupOptions.style.display = "none";
    manualSetup.style.display = "none";
    autoSetup.style.display = "none";
    whatsappSetup.style.display = "none";

    if (platformSelect.value === "2") {  // Telegram
        setupOptions.style.display = "block";
    } else if (platformSelect.value === "4") {  // WhatsApp
        whatsappSetup.style.display = "block";
    }
}

// Функция для отображения полей установки Telegram (ручной/автоматический)
function toggleFields() {
    const setupMode = document.getElementById('setup_mode').value;
    document.getElementById('manual-setup').style.display = setupMode === "manual" ? "block" : "none";
    document.getElementById('auto-setup').style.display = setupMode === "auto" ? "block" : "none";
}
