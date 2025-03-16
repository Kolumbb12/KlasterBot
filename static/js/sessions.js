document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[id^='qr-container-']").forEach(container => {
        let sessionId = container.id.replace("qr-container-", "").trim(); // Получаем session_id

        if (!sessionId) {
            console.error("Ошибка: sessionId не найден для контейнера", container);
            return;
        }

        let qrImg = document.getElementById(`qr-img-${sessionId}`);
        let qrText = container.querySelector("p");

        console.log(`Запрос QR-кода для session_id: ${sessionId}`);

        fetch(`/get_qr/${sessionId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`QR-код не найден для session_id: ${sessionId}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.qr_code) {
                    qrImg.src = "data:image/png;base64," + data.qr_code;
                    qrImg.style.display = "block";
                    qrText.style.display = "none";
                } else {
                    qrText.textContent = "QR-код не найден.";
                }
            })
            .catch(error => {
                console.error(`Ошибка загрузки QR-кода для сессии ${sessionId}:`, error);
                qrText.textContent = "Ошибка загрузки QR-кода.";
            });
    });
});