"""
session_routes.py
Модуль маршрутов (роутов) для управления сессиями. Содержит функции для:
- Отображения списка активных сессий.
- Назначения платформы для агента.
- Создания новой сессии.
- Завершения активной сессии.
"""

import asyncio
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from database.db_functions import *
from application.services.telegram.bot_manager import bot_manager
from utils.logs.logger import logger


# Создаём Blueprint для маршрутов, связанных с управлением сессиями
session_bp = Blueprint('session_bp', __name__)


# Маршрут для отображения страницы выбора платформы для агента
@session_bp.route('/sessions/assign/<int:agent_id>', methods=['GET'])
def assign_platform(agent_id):
    """
    Отображение страницы для назначения платформы агенту.
    """
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('user_bp.login'))
    try:
        agent = select_agent_by_id(agent_id)  # Получение информации об агенте
        platforms = get_available_platforms(agent_id)  # Получение списка доступных платформ
        return render_template('assign_platform.html', agent=agent, platforms=platforms)
    except Exception as e:
        flash(f"Ошибка при загрузке страницы назначения платформы: {e}", "error")
        return redirect(url_for('session_bp.sessions'))


# Маршрут для создания новой сессии
@session_bp.route('/sessions/create/<int:agent_id>', methods=['POST'])
def create_session(agent_id):
    """
    Создание новой сессии для агента.
    """
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('user_bp.login'))
    try:
        user_id = session['user_id']
        platform_id = int(request.form.get('platform'))  # Получение chat_type_id из формы
        api_token = request.form.get('api_token', '').strip()  # Получение токена платформы

        # Проверка на обязательность токена для Telegram (bot)
        if platform_id == 2 and not api_token:
            flash("Для Telegram (bot) необходимо указать токен.", "error")
            return redirect(url_for('session_bp.assign_platform', agent_id=agent_id))

        # Создание новой сессии
        session_id = add_session(user_id, agent_id, platform_id, api_token)

        flash("Сессия успешно создана.", "success")
        return redirect(url_for('session_bp.sessions'))

    except Exception as e:
        flash(f"Ошибка при создании сессии: {e}", "error")
        return redirect(url_for('session_bp.sessions'))



# Маршрут для отображения списка активных сессий
@session_bp.route('/sessions', methods=['GET'])
def sessions():
    """
    Отображение всех активных сессий текущего пользователя.
    """
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('user_bp.login'))  # Убедитесь, что 'user_bp.login' корректен

    try:
        user_id = session.get('user_id')  # Получение ID текущего пользователя
        user_sessions = get_user_sessions(user_id)  # Получение списка сессий пользователя

        # Если сессии не найдены, просто показываем пустую таблицу
        if user_sessions is None:
            user_sessions = []

        return render_template('sessions.html', user_sessions=user_sessions)

    except Exception as e:
        # Перенаправляем на страницу дэшборда, если произошла ошибка
        flash(f"Ошибка при загрузке списка сессий: {e}", "error")
        return redirect(url_for('agent_bp.agent_selection'))  # Избегаем перенаправления на сам /sessions


# Маршрут для активации сессии
@session_bp.route('/sessions/activate/<int:session_id>', methods=['POST'])
def activate_session(session_id):
    """
    Активация сессии.
    """
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('user_bp.login'))

    try:
        session_data = get_session_by_id(session_id)
        if not session_data:
            flash("Сессия не найдена.", "error")
            return redirect(url_for('session_bp.sessions'))

        # Запускаем бота
        try:
            bot_manager.start_bot(session_id, session_data['api_token'])
        except Exception as e:
            logger.log(f"Ошибка при отрабатавании роута activate: {e}", "ERROR")

        if activate_session_in_db(session_id):
            flash("Сессия успешно активирована.", "success")
        else:
            flash("Ошибка при обновлении статуса сессии в базе данных.", "error")

        return redirect(url_for('session_bp.sessions'))
    except Exception as e:
        flash(f"Ошибка: {e}", "error")
        return redirect(url_for('session_bp.sessions'))


# Маршрут для завершения активной сессии
@session_bp.route('/sessions/terminate/<int:session_id>', methods=['POST'])
def terminate_session(session_id):
    """
    Завершение активной сессии.
    """
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('user_bp.login'))
    try:
        session_data = get_session_by_id(session_id)
        if not session_data:
            flash("Сессия не найдена.", "error")
            return redirect(url_for('session_bp.sessions'))

        try:
            bot_manager.stop_bot(session_id)
        except Exception as e:
            logger.log(f"Ошибка при отрабатавании роута terminate: {e}", "ERROR")

        if terminate_session_in_db(session_id):  # Меняем статус в БД только после успешной остановки бота
            flash("Сессия успешно диактивирована.", "success")
        else:
            flash("Ошибка при обновлении статуса сессии в базе данных.", "error")

        return redirect(url_for('session_bp.sessions'))
    except Exception as e:
        flash(f"Ошибка при завершении сессии: {e}", "error")
        return redirect(url_for('session_bp.sessions'))


@session_bp.route('/sessions/configure/<int:session_id>', methods=['GET'])
def configure_session(session_id):
    """
    Настройка сессии.
    """
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('user_bp.login'))

    try:
        session_data = get_session_by_id(session_id)
        if not session_data:
            flash("Сессия не найдена.", "error")
            return redirect(url_for('session_bp.sessions'))

        # Логика для получения данных настройки сессии
        return render_template('configure_session.html', session=session_data)

    except Exception as e:
        flash(f"Ошибка при настройке сессии: {e}", "error")
        return redirect(url_for('session_bp.sessions'))
