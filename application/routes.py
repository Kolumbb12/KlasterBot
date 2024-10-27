from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from database.db_connection import create_server_connection

main = Blueprint('main', __name__)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Подключение к базе данных и поиск пользователя
        connection = create_server_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        # Проверка существования пользователя и соответствия пароля
        if user and user['password'] == password:  # Упростил проверку пароля без хэширования
            session['user_id'] = user['id']
            session['is_admin'] = bool(user['is_admin'])

            flash('Вы успешно вошли на сайт', 'success')
            return redirect(url_for('main.agent_selection'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')

    return render_template('login.html')


@main.route('/agent_selection')
def agent_selection():
    # Проверка авторизации
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('main.login'))

    return render_template('agent_selection.html')


@main.route('/agent_settings')
def agent_settings():
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('main.login'))

    return render_template('agent_settings.html')


@main.route('/chat')
def chat():
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('main.login'))

    return render_template('chat.html')


@main.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('main.login'))
