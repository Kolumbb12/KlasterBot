from database.db_functions import *
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

        # Перенести в отдельную функцию
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        # Проверка существования пользователя и соответствия пароля
        if user and user['password'] == password:  # Упростил проверку пароля без хеширования
            session['user_id'] = user['id']
            session['is_admin'] = bool(user['is_admin'])

            flash('Вы успешно вошли на сайт', 'success')
            return redirect(url_for('main.agent_selection'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')

    return render_template('login.html')


@main.route('/agent_selection')
def agent_selection():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    user_id = session['user_id']
    agents = select_all_agents_by_user_id(user_id)
    return render_template('agent_selection.html', agents=agents)


@main.route('/agent_settings', methods=['GET', 'POST'])
@main.route('/agent_settings/<int:agent_id>', methods=['GET', 'POST'])
def agent_settings(agent_id=None):
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('main.login'))

    agent = select_agent_by_id(agent_id) if agent_id else None

    if request.method == 'POST':
        name = request.form['name']
        instruction = request.form['instruction']
        temperature = float(request.form['temperature']) / 100  # Конвертируем значение из диапазона 0-100 в 0-1
        max_tokens = int(request.form['max_tokens'])
        message_buffer = int(request.form['message_buffer'])
        accumulate_messages = 'accumulate_messages' in request.form
        transmit_date = 'transmit_date' in request.form
        api_key = request.form['api_key']

        settings = {
            'name': name,
            'instruction': instruction,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'message_buffer': message_buffer,
            'accumulate_messages': accumulate_messages,
            'transmit_date': transmit_date,
            'api_key': api_key
        }

        if agent:
            update_agent_settings(agent_id, settings)
            flash("Настройки агента обновлены", "success")
        else:
            insert_agent(
                name=name,
                user_id=session['user_id'],
                instruction=instruction,
                temperature=temperature,
                max_tokens=max_tokens,
                message_buffer=message_buffer,
                accumulate_messages=accumulate_messages,
                transmit_date=transmit_date,
                api_key=api_key
            )
            flash("Агент создан", "success")
        return redirect(url_for('main.agent_selection'))
    return render_template('agent_settings.html', agent=agent)

@main.route('/toggle_agent_status/<int:agent_id>')
def toggle_agent_status(agent_id):
    # Получаем текущий статус агента
    agent = select_agent_by_id(agent_id)

    if agent:
        # Переключаем статус
        new_status = not agent['is_active']
        set_agent_active_status(agent_id, new_status)
        flash(f"Агент {'включен' if new_status else 'выключен'}.", "success")
    else:
        flash("Агент не найден.", "error")

    return redirect(url_for('main.agent_selection'))


@main.route('/chat')
def chat():
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('main.login'))

    return render_template('chat.html')


@main.route('/logout')
def logout():
    session.clear()  # Очистка сессии
    flash("Вы вышли из аккаунта.", "info")
    return redirect(url_for('main.login'))  # Перенаправление на страницу входа



