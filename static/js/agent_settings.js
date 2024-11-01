function updateTemperatureDisplay() {
    const temperatureSlider = document.getElementById('temperature');
    const temperatureDisplay = document.getElementById('temperature-value');
    temperatureDisplay.textContent = temperatureSlider.value + '%';
}

// Инициализируем отображение текущего значения температуры при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    updateTemperatureDisplay();
    document.getElementById('temperature').addEventListener('input', updateTemperatureDisplay);
});

document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.getElementById('bot-instruction');

    textarea.addEventListener('input', function() {
        this.style.height = 'auto'; // Сбрасывает высоту, чтобы изменить ее
        this.style.height = (this.scrollHeight) + 'px'; // Устанавливает высоту в зависимости от содержимого
    });

    // Инициализация высоты при загрузке страницы, если есть текст
    if (textarea.value) {
        textarea.style.height = 'auto';
        textarea.style.height = (textarea.scrollHeight) + 'px';
    }
});
