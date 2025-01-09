"""
agent_routes.py
Модуль маршрутов для управления агентами. Включает маршруты для отображения списка агентов, создания и редактирования
агентов, изменения их статуса и получения данных агента.
"""

from database.db_functions import *
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from utils.gpt_api import validate_api_key
from utils.access_control import has_access, limiter, custom_limit_key


# Создаем blueprint для маршрутов, связанных с агентами
agent_bp = Blueprint('agent_bp', __name__)


@agent_bp.route('/agent_selection')
@limiter.limit("5 per minute", key_func=custom_limit_key)
def agent_selection():
    """
    Маршрут для отображения списка агентов текущего пользователя.

    Если пользователь администратор, отображаются также агенты всех других пользователей.
    """
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('user_bp.login'))
    user_id = session['user_id']
    agents = get_all_agents_by_user_id(user_id)
    # Если пользователь администратор, добавляем всех агентов, кроме его собственных
    other_agents = []
    if session.get('role_id') == 1:
        other_agents = get_all_agents_except_user(user_id)

    return render_template('agent_selection.html', agents=agents, other_agents=other_agents)


@agent_bp.route('/agent_settings', methods=['GET', 'POST'])
@agent_bp.route('/agent_settings/<int:agent_id>', methods=['GET', 'POST'])
@limiter.limit("5 per minute", key_func=custom_limit_key)
def agent_settings(agent_id=None):
    """
    Маршрут для создания и редактирования настроек агента.

    Обрабатывает GET и POST запросы:
    - GET: Отображает страницу с формой для создания или редактирования агента.
    - POST: Обрабатывает отправленную форму для создания нового агента или обновления существующего.

    :param agent_id: Идентификатор агента для редактирования (опционально).
    :return: Шаблон agent_settings.html для GET-запросов или перенаправление на agent_selection после сохранения.
    """
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('user_bp.login'))

    if agent_id is not None:
        if not has_access(agent_id, 'agent', session['user_id'], session.get('role_id')):
            flash("У вас нет прав на доступ к этому агенту.", "error")
            return redirect(url_for('agent_bp.agent_selection'))

    agent = get_agent_by_id(agent_id) if agent_id else None
    page_title = "Настройки агента" if agent else "Создание агента"

    if request.method == 'POST':
        name = request.form.get('name')
        instruction = request.form.get('instruction')
        start_message = request.form.get('start_message')
        error_message = request.form.get('error_message')
        temperature = float(request.form.get('temperature')) / 100  # Конвертируем значение из диапазона 0-100 в 0-1
        max_tokens = request.form.get('max_tokens')
        api_key = request.form.get('api_key')
        # Проверка на отсутствие обязательных полей
        if not all([name, instruction, start_message, error_message, api_key]):
            flash("Все поля должны быть заполнены корректно!", "error")
            return redirect(url_for('agent_bp.agent_settings', agent_id=agent_id))
        # Проверка на отрицательные значения
        if int(max_tokens) < 0:
            flash("Максимальное количество токенов не может быть отрицательными.", "error")
            return redirect(url_for('agent_bp.agent_settings', agent_id=agent_id))
        # Проверка валидности API Key
        if not validate_api_key(api_key):
            flash("API Key недействителен. Проверьте корректность ключа.", "error")
            return redirect(url_for('agent_bp.agent_settings', agent_id=agent_id))
        # Преобразование значений для базы данных
        max_tokens = int(max_tokens)
        settings = {
            'name': name,
            'instruction': instruction,
            'start_message': start_message,
            'error_message': error_message,
            'temperature': temperature,
            'max_tokens': max_tokens,
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
                api_key=api_key
            )
            flash("Агент создан", "success")
        return redirect(url_for('agent_bp.agent_selection'))
    return render_template('agent_settings.html', agent=agent, page_title=page_title)


@agent_bp.route('/toggle_agent_status/<int:agent_id>')
@limiter.limit("5 per minute", key_func=custom_limit_key)
def toggle_agent_status(agent_id):
    """
    Маршрут для изменения статуса агента (включен/выключен).

    Обрабатывает GET запрос:
    - GET: Переключает статус активности агента и перенаправляет на страницу выбора агентов.

    :param agent_id: Идентификатор агента, статус которого нужно изменить.
    :return: Перенаправление на страницу agent_selection.
    """
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('user_bp.login'))
    # Получаем текущий статус агента
    agent = get_agent_by_id(agent_id)
    if agent:
        # Переключаем статус
        new_status = not agent['is_active']
        set_agent_active_status(agent_id, new_status)
        flash(f"Агент {'включен' if new_status else 'выключен'}.", "success")
    else:
        flash("Агент не найден.", "error")

    return redirect(url_for('agent_bp.agent_selection'))


@agent_bp.route('/get_agent_data/<int:agent_id>', methods=['GET'])
@limiter.limit("5 per minute", key_func=custom_limit_key)
def get_agent_data(agent_id):
    """
    Маршрут для получения данных агента в формате JSON.

    Обрабатывает GET запрос:
    - GET: Возвращает данные агента, включая имя, сообщения и статус активности.

    :param agent_id: Идентификатор агента, данные которого нужно получить.
    :return: JSON с данными агента или сообщение об ошибке, если агент не найден.
    """
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('user_bp.login'))
    agent = get_agent_by_id(agent_id)
    if agent:
        data = {
            "name": agent['name'],
            "start_message": agent['start_message'] or "Привет, чем могу помочь?",
            "error_message": agent['error_message'] or "Извините, агент недоступен.",
            "is_active": agent['is_active']
        }
        return jsonify(data)
    return jsonify({"error": "Агент не найден"}), 404
