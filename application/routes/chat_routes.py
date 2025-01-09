"""
chat_routes.py
Модуль маршрутов (роутов) для управления функционалом чата. Включает маршруты для взаимодействия с ботом,
получения истории чата и очистки чата. Использует подключение к базе данных для хранения и извлечения сообщений.
Также используется для отображения переписок пользователей и сессий (ботов).
"""

from database.db_functions import *
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from utils.gpt_api import generate_response
from utils.access_control import has_access, limiter, custom_limit_key


# Создаем blueprint для маршрутов, связанных с чатом
chat_bp = Blueprint('chat_bp', __name__)


@chat_bp.route('/chat', methods=['GET', 'POST'])
@limiter.limit("5 per minute", key_func=custom_limit_key)
def chat():
    """
    Маршрут для взаимодействия с ботом в чате.

    Обрабатывает GET и POST запросы:
    - GET: Отображает страницу чата с агентами и историей чата.
    - POST: Обрабатывает сообщение от пользователя, отправляет его боту и возвращает ответ.

    :return: Шаблон chat.html для GET-запросов или JSON с ответом бота для POST-запросов.
    """
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('user_bp.login'))

    user_id = session['user_id']

    if request.method == 'GET':
        agent_id = request.args.get('agent_id', type=int, default=1)  # Определение agent_id из параметров запроса
        agents = get_all_agents_by_user_id(user_id)
        my_chat_history = get_chat_history_by_user_and_agent(user_id=user_id, agent_id=agent_id,
                                                             chat_type_id=1) or []  # Убедитесь, что chat_history не None
        return render_template('chat.html', agents=agents, chat_history=my_chat_history, selected_agent_id=agent_id)

    elif request.method == 'POST':
        data = request.get_json()
        agent_id = data.get('agent_id')
        chat_type_id = data.get('chat_type_id')
        user_input = data.get('message')
        if not agent_id or not user_input:
            return jsonify({"error": "Требуются ID агента и сообщение"}), 400

        try:
            # Получаем и обновляем историю чата из базы данных
            my_chat_history = get_chat_history_by_user_and_agent(user_id, agent_id, chat_type_id) or []
            response = generate_response(agent_id, user_input, my_chat_history)
            # Сохраняем сообщение пользователя и ответ бота в базу данных
            insert_chat_message(user_id, agent_id, chat_type_id, user_input, response)
            return jsonify({"response": response})

        except Exception as e:
            return jsonify({"error": str(e)}), 500


@chat_bp.route('/chat_history', methods=['GET'])
@limiter.limit("5 per minute", key_func=custom_limit_key)
def chat_history():
    """
    Маршрут для получения истории чата с определенным агентом.

    Обрабатывает GET запрос:
    - GET: Возвращает историю чата с указанным агентом в формате JSON.

    :return: JSON с историей чата или сообщение об ошибке.
    """
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('user_bp.login'))

    agent_id = request.args.get('agent_id')
    if not agent_id:
        return jsonify({"error": "ID агента не указан"}), 400
    try:
        user_id = session['user_id']
        my_chat_history = get_chat_history_by_user_and_agent(user_id, agent_id, 1)
        return jsonify({"chat_history": my_chat_history}), 200
    except Exception as e:
        print(f"Ошибка при получении истории чата: {e}")
        return jsonify({"error": "Ошибка при получении истории чата"}), 500


@chat_bp.route('/clear_chat', methods=['POST'])
@limiter.limit("5 per minute", key_func=custom_limit_key)
def clear_chat():
    """
    Маршрут для очистки истории чата с определенным агентом.

    Обрабатывает POST запрос:
    - POST: Удаляет историю чата с указанным агентом для текущего пользователя.

    :return: JSON с сообщением об успешной очистке или сообщение об ошибке.
    """
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('user_bp.login'))

    user_id = session['user_id']
    data = request.get_json()
    agent_id = data.get('agent_id')
    chat_type_id = data.get('chat_type_id')

    if not agent_id or not chat_type_id:
        return jsonify({"error": "Требуются ID агента и тип чата"}), 400

    try:
        delete_chat_history(user_id=user_id, agent_id=agent_id, chat_type_id=chat_type_id)
        return jsonify({"success": "Чат успешно очищен"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route('/all_chats', methods=['GET'])
@limiter.limit("5 per minute", key_func=custom_limit_key)
def all_chats():
    """
    Маршрут для просмотра чатов администратором.
    """
    # Проверяем, что пользователь администратор
    if 'user_id' not in session:
        flash('Пожалуйста авторизуйтесь.', 'error')
        return redirect(url_for('user_bp.login'))

    # Получаем session_id и user_id из параметров запроса
    session_id = request.args.get('session_id', type=int)
    user_id = request.args.get('user_id', type=int)

    # Проверка доступа к сессии
    if session_id and not has_access(session_id, 'session', session['user_id'], session.get('role_id')):
        flash("У вас нет прав на доступ к этой сессии.", "error")
        return redirect(url_for('chat_bp.all_chats'))

    # Проверка доступа к чатам
    if user_id and not has_access(user_id, 'user', session['user_id'], session.get('role_id')):
        flash("У вас нет прав на просмотр чатов этого пользователя.", "error")
        return redirect(url_for('chat_bp.all_chats'))

    try:
        # Загружаем пользователей и историю чатов
        users = []
        user_chat_history = []
        if session_id:
            users = get_users_by_session_id(session_id)

        if session_id and user_id:
            user_chat_history = get_chat_history_by_session_id_and_user_id(session_id, user_id)

        # Загружаем список сессий
        if session['role_id'] == 1:
            sessions = get_all_sessions()
        else:
            sessions = get_user_sessions(session['user_id'])

        return render_template(
            'all_chats.html',
            users=users,
            sessions=sessions,
            chat_history=user_chat_history,
            selected_user_id=user_id,
            selected_session_id=session_id,
        )
    except Exception as e:
        flash(f"Ошибка: {e}", "error")
        return redirect(url_for('chat_bp.all_chats'))


@chat_bp.route('/users_by_session', methods=['GET'])
@limiter.limit("5 per minute", key_func=custom_limit_key)
def users_by_session():
    """
    Возвращает пользователей с историей чата по session_id.
    """
    session_id = request.args.get('session_id', type=int)
    if not session_id:
        return jsonify({"error": "Не указан session_id"}), 400

    try:
        users = get_users_by_session_id(session_id)
        return jsonify({"users": users}), 200
    except Exception as e:
        return jsonify({"error": f"Ошибка при загрузке пользователей: {e}"}), 500
