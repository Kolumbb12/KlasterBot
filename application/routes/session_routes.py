"""
session_routes.py
Модуль маршрутов (роутов) для управления сессиями. Содержит функции для:
- Отображения списка активных сессий.
- Назначения платформы для агента.
- Создания новой сессии.
- Завершения активной сессии.
"""

import asyncio
from asyncio import run_coroutine_threadsafe
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from database.db_functions import *
from application.services.telegram.bot_manager import bot_manager
from utils.logs.logger import logger
from utils.utils import create_update_from_json
from aiogram.types import Update
from flask import current_app


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
        flash(f"Ошибка при загрузке списка сессий: {e}", "error")
        return redirect(url_for('agent_bp.agent_selection'))  # Избегаем перенаправления на сам /sessions


@session_bp.route('/webhook/<int:session_id>', methods=['POST'])
def webhook(session_id):
    """
    Обработка обновлений от Telegram.
    """
    bot_runner = bot_manager.get_bot(session_id)
    if not bot_runner:
        logger.log(f"Bot for session {session_id} not found", level="ERROR")
        return jsonify({"error": "Bot not found"}), 404

    # Получаем JSON-данные из запроса
    update_data = request.get_json()

    try:
        # Преобразуем JSON-данные в объект Update с помощью собственной функции
        update = create_update_from_json(update_data)

        # Обрабатываем обновление через диспетчер
        loop = current_app.config["event_loop"]  # Используем event_loop из конфигурации Flask
        asyncio.run_coroutine_threadsafe(
            bot_runner.dp.feed_update(bot_runner.bot, update), loop
        )
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.log(f"Error processing webhook for session {session_id}: {str(e)}", level="ERROR")
        return jsonify({"error": str(e)}), 500


@session_bp.route('/sessions/activate/<int:session_id>', methods=['POST'])
def activate_session(session_id):
    """
    Активация сессии (запуск бота).
    """
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('user_bp.login'))
    try:
        user_session = get_session_by_id(session_id)
        if user_session:
            token = user_session['api_token']
            port = 5001 + session_id
            asyncio.run_coroutine_threadsafe(bot_manager.start_bot(session_id, token, port), current_app.config["event_loop"])
            activate_session_in_db(session_id)
            flash(f"Сессия {session_id} успешно активирована!", "success")
        else:
            flash(f"Сессия {session_id} не найдена.", "error")
    except Exception as e:
        logger.log(f"Ошибка при активации сессии {session_id}: {e}", "ERROR")
        flash(f"Ошибка при активации сессии {session_id}: {e}", "error")
    return redirect(url_for('session_bp.sessions'))


@session_bp.route('/sessions/terminate/<int:session_id>', methods=['POST'])
def terminate_session(session_id):
    """
    Деактивация сессии (остановка бота).
    """
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('user_bp.login'))
    try:
        asyncio.run_coroutine_threadsafe(bot_manager.stop_bot(session_id), current_app.config["event_loop"])
        terminate_session_in_db(session_id)
        flash(f"Сессия {session_id} успешно завершена!", "success")
    except Exception as e:
        logger.log(f"Ошибка при завершении сессии {session_id}: {e}", "ERROR")
        flash(f"Ошибка при завершении сессии {session_id}: {e}", "error")
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
        user_session = get_session_by_id(session_id)
        if not user_session:
            flash("Сессия не найдена.", "error")
            return redirect(url_for('session_bp.sessions'))

        # Логика для получения данных настройки сессии
        return render_template('configure_session.html', user_session=user_session)

    except Exception as e:
        flash(f"Ошибка при настройке сессии: {e}", "error")
        return redirect(url_for('session_bp.sessions'))
