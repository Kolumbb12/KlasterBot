document.addEventListener("DOMContentLoaded", function () {
    document.getElementById('platform').addEventListener('change', toggleSetupMode);
    document.getElementById('setup_mode').addEventListener('change', toggleFields);
    document.querySelector('form').addEventListener('submit', function(event) {
        validateForm(event);
    });
});

function validateForm(event) {
    const platformSelect = document.getElementById('platform');
    const tokenInput = document.getElementById('api_token');
    const phoneNumberInput = document.getElementById('whatsapp_phone_number');

    if (platformSelect.value === "2") {
        const token = tokenInput.value.trim();
        const tokenRegex = /^\d{8,10}:[A-Za-z0-9_-]{35,}$/;
        if (!tokenRegex.test(token)) {
            showErrorMessage("Введите корректный токен Telegram!");
            event.preventDefault();
            return false;
        }
    }

    if (platformSelect.value === "4") {
        let phoneNumber = phoneNumberInput.value.trim();
        if (!phoneNumber.startsWith('+')) {
            phoneNumber = '+' + phoneNumber;
            phoneNumberInput.value = phoneNumber;
        }

        const phoneRegex = /^\+\d{11,15}$/;
        if (!phoneRegex.test(phoneNumber)) {
            showErrorMessage("Введите корректный номер телефона в формате +77012345678.");
            event.preventDefault();
            return false;
        }
    }

    hideErrorMessage();
    return true;
}

function showErrorMessage(message) {
    const errorMessage = document.getElementById('error-message');
    errorMessage.innerText = message;
    errorMessage.style.display = "block";
}

function hideErrorMessage() {
    const errorMessage = document.getElementById('error-message');
    errorMessage.style.display = "none";
}

function toggleSetupMode() {
    const platformSelect = document.getElementById('platform');
    const setupOptions = document.getElementById('setup-options');
    const manualSetup = document.getElementById('manual-setup');
    const autoSetup = document.getElementById('auto-setup');
    const whatsappSetup = document.getElementById('whatsapp-setup');

    const phoneNumberInput = document.getElementById('whatsapp_phone_number');
    const botNameInput = document.getElementById('whatsapp_bot_name');

    // Скрываем все блоки
    setupOptions.style.display = "none";
    manualSetup.style.display = "none";
    autoSetup.style.display = "none";
    whatsappSetup.style.display = "none";

    phoneNumberInput.removeAttribute("required");
    botNameInput.removeAttribute("required");

    if (platformSelect.value === "2") {
        setupOptions.style.display = "block";
    } else if (platformSelect.value === "4") {
        whatsappSetup.style.display = "block";
        phoneNumberInput.setAttribute("required", "true");
        botNameInput.setAttribute("required", "true");
    }
}

function toggleFields() {
    const setupMode = document.getElementById('setup_mode').value;
    document.getElementById('manual-setup').style.display = setupMode === "manual" ? "block" : "none";
    document.getElementById('auto-setup').style.display = setupMode === "auto" ? "block" : "none";
}
