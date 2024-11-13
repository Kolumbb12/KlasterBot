document.querySelector('form').addEventListener('submit', function (e) {
    const newPassword = document.getElementById('new_password').value;
    const confirmPassword = document.getElementById('confirm_password').value;

    if (newPassword !== confirmPassword) {
        e.preventDefault();
        alert("Пароли не совпадают.");
    }
});