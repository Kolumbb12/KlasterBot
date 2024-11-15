/*
agent_settings.js
Этот файл содержит JavaScript-код для управления настройками агента на странице.
В частности, он включает функции для динамического обновления отображаемого значения температуры,
а также для автоматической регулировки высоты текстовой области, используемой для инструкций агента.

Основные компоненты:
1. `updateTemperatureDisplay()`: Функция для обновления отображаемого значения температуры в процентах при
перемещении ползунка.
2. События `DOMContentLoaded`: Обработчики, которые запускают функции при загрузке страницы,
в том числе для установки начального значения температуры и высоты текстовой области.
*/

// Функция для обновления отображаемого значения температуры
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

// Регулировка высоты текстовой области в зависимости от содержимого
document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.getElementById('bot-instruction');

    textarea.addEventListener('input', function() {
        this.style.height = 'auto'; // Сбрасывает высоту, чтобы пересчитать
        this.style.height = (this.scrollHeight) + 'px'; // Устанавливает высоту в зависимости от содержимого
    });

    // Инициализация высоты при загрузке страницы, если текст уже присутствует
    if (textarea.value) {
        textarea.style.height = 'auto';
        textarea.style.height = (textarea.scrollHeight) + 'px';
    }
});
