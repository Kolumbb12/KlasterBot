"""
chat_routes.py
Модуль маршрутов (роутов) для управления функционалом чата. Включает маршруты для взаимодействия с ботом,
получения истории чата и очистки чата. Использует подключение к базе данных для хранения и извлечения сообщений.
"""

from database.db_functions import *
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from web_clients.gpt_api import generate_response


# Создаем blueprint для маршрутов, связанных с чатом
chat_bp = Blueprint('chat_bp', __name__)


@chat_bp.route('/chat', methods=['GET', 'POST'])
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
        agents = select_all_agents_by_user_id(user_id)
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
        # Логика получения истории чата из базы данных
        my_chat_history = get_chat_history_by_user_and_agent(user_id, agent_id, 1)
        return jsonify({"chat_history": my_chat_history}), 200
    except Exception as e:
        print(f"Ошибка при получении истории чата: {e}")
        return jsonify({"error": "Ошибка при получении истории чата"}), 500


@chat_bp.route('/clear_chat', methods=['POST'])
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
