/*
change_password.js
Этот файл содержит JavaScript-код для страницы смены пароля.
Он добавляет проверку совпадения нового пароля и подтверждения пароля перед отправкой формы.

Основной компонент:
1. Обработчик события `submit` для формы, который проверяет совпадение полей "Новый пароль" и "Подтвердите пароль".
Если пароли не совпадают, отправка формы блокируется, и пользователю отображается предупреждение.
*/

// Добавляем обработчик события отправки формы
document.querySelector('form').addEventListener('submit', function (e) {
    const newPassword = document.getElementById('new_password').value;
    const confirmPassword = document.getElementById('confirm_password').value;

    // Проверка на совпадение нового пароля и подтверждения
    if (newPassword !== confirmPassword) {
        e.preventDefault(); // Блокируем отправку формы
        alert("Пароли не совпадают."); // Выводим предупреждение пользователю
    }
});
