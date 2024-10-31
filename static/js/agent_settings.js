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