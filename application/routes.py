from database.db_functions import *
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
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
    page_title = "Настройки агента" if agent else "Создание агента"

    if request.method == 'POST':
        name = request.form.get('name')
        instruction = request.form.get('instruction')
        start_message = request.form.get('start_message')
        error_message = request.form.get('error_message')
        temperature = float(request.form.get('temperature')) / 100  # Конвертируем значение из диапазона 0-100 в 0-1
        max_tokens = request.form.get('max_tokens')
        message_buffer = request.form.get('message_buffer')
        accumulate_messages = 'accumulate_messages' in request.form
        transmit_date = 'transmit_date' in request.form
        api_key = request.form.get('api_key')

        # Проверка на отсутствие обязательных полей
        if not all([name, instruction, start_message, error_message, api_key]):
            flash("Все поля должны быть заполнены корректно!", "error")
            return redirect(url_for('main.agent_settings', agent_id=agent_id))

        # Проверка на отрицательные значения
        if int(max_tokens) < 0 or int(message_buffer) < 0:
            flash("Максимальное количество токенов и буфер сообщений не могут быть отрицательными.", "error")
            return redirect(url_for('main.agent_settings', agent_id=agent_id))

        # Преобразование значений для базы данных
        max_tokens = int(max_tokens)
        message_buffer = int(message_buffer)

        settings = {
            'name': name,
            'instruction': instruction,
            'start_message': start_message,
            'error_message': error_message,
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
                start_message=start_message,
                error_message=error_message,
                temperature=temperature,
                max_tokens=max_tokens,
                message_buffer=message_buffer,
                accumulate_messages=accumulate_messages,
                transmit_date=transmit_date,
                api_key=api_key
            )
            flash("Агент создан", "success")
        return redirect(url_for('main.agent_selection'))
    return render_template('agent_settings.html', agent=agent, page_title=page_title)

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

    user_id = session['user_id']
    agents = select_all_agents_by_user_id(user_id)
    return render_template('chat.html', agents=agents)


@main.route('/get_agent_data/<int:agent_id>', methods=['GET'])
def get_agent_data(agent_id):
    agent = select_agent_by_id(agent_id)
    if agent:
        data = {
            "name": agent['name'],
            "start_message": agent['start_message'] or "Привет, чем могу помочь?",
            "error_message": agent['error_message'] or "Извините, агент недоступен.",
            "is_active": agent['is_active']
        }
        return jsonify(data)
    return jsonify({"error": "Агент не найден"}), 404



@main.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if not session.get('is_admin'):
        flash("У вас нет прав доступа", "error")
        return redirect(url_for('main.agent_selection'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_admin = 'is_admin' in request.form

        if username and password:
            insert_user(username=username, password=password, is_admin=int(is_admin))
            flash("Пользователь успешно добавлен", "success")
            return redirect(url_for('main.agent_selection'))
        else:
            flash("Заполните все поля", "error")

    return render_template('add_user.html')


@main.route('/logout')
def logout():
    session.clear()  # Очистка сессии
    flash("Вы вышли из аккаунта.", "info")
    return redirect(url_for('main.login'))  # Перенаправление на страницу входа



