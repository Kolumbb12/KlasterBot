"""
session_routes.py
Модуль маршрутов (роутов) для управления сессиями. Содержит функции для:
- Отображения списка активных сессий.
- Назначения платформы для агента.
- Создания новой сессии.
- Активации сессии.
- Завершения активной сессии.
- Конфигурации сессии.
"""

import asyncio
from asyncio import run_coroutine_threadsafe
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from database.db_functions import *
from application.services.telegram.bot_manager import bot_manager
from utils.logs.logger import logger
from utils.utils import create_update_from_json, get_telegram_bot_name_and_username_by_token
from aiogram.types import Update
from flask import current_app
from application.services.telegram.bot_configurator import *
from werkzeug.utils import secure_filename
from utils.access_control import has_access, limiter, custom_limit_key


# Создаём Blueprint для маршрутов, связанных с управлением сессиями
session_bp = Blueprint('session_bp', __name__)


@session_bp.route('/sessions/assign/<int:agent_id>', methods=['GET'])
@limiter.limit("5 per minute", key_func=custom_limit_key)
def assign_platform(agent_id):
    """
    Отображение страницы для назначения платформы агенту.
    """
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('user_bp.login'))
    if not has_access(agent_id, 'agent', session['user_id'], session.get('role_id')):
        flash("У вас нет прав на доступ к этому агенту.", "error")
        return redirect(url_for('agent_bp.agent_selection'))
    try:
        agent = get_agent_by_id(agent_id)
        platforms = get_available_platforms(agent_id)
        return render_template('assign_platform.html', agent=agent, platforms=platforms)
    except Exception as e:
        flash(f"Ошибка при загрузке страницы назначения платформы: {e}", "error")
        return redirect(url_for('session_bp.sessions'))


@session_bp.route('/sessions/create/<int:agent_id>', methods=['POST'])
@limiter.limit("5 per minute", key_func=custom_limit_key)
def create_session(agent_id):
    """
    Создание новой сессии для агента.
    """
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('user_bp.login'))
    try:
        user_id = session['user_id']
        platform_id = int(request.form.get('platform'))
        setup_mode = request.form.get('setup_mode')  # Ручная или автоматическая установка

        # Если выбран Telegram (Бот)
        if platform_id == 2:
            # Если выбрана ручная установка, токен обязателен
            if setup_mode == "manual":
                api_token = request.form.get('api_token', '').strip()
                if not api_token:
                    flash("Для Telegram (бот) при ручной установке необходимо указать токен.", "error")
                    return redirect(url_for('session_bp.assign_platform', agent_id=agent_id))
                if not is_valid_telegram_token(api_token):
                    flash("Указан не валидный токен. Пожалуйста, укажите корректный токен.", "error")
                    return redirect(url_for('session_bp.assign_platform', agent_id=agent_id))
                if is_telegram_token_api_exists(api_token):
                    flash("Указанный токен уже используется. Пожалуйста, укажите другой.", "error")
                    return redirect(url_for('session_bp.assign_platform', agent_id=agent_id))
                bot_name, bot_username = get_telegram_bot_name_and_username_by_token(api_token)
            # Если выбрана автоматическая установка
            if setup_mode == "auto":
                bot_name = request.form.get('bot_name')
                bot_username = request.form.get('bot_username')
                # Проверка обязательных полей
                if not bot_name or not bot_username:
                    flash("Наименование и username бота обязательны для автоматической установки.", "error")
                    return redirect(url_for('session_bp.assign_platform', agent_id=agent_id))
                # Создание бота
                api_token = run_async_task(create_bot(bot_name, bot_username))
                if "Ошибка" in api_token:
                    flash(api_token, "error")
                    return redirect(url_for('session_bp.assign_platform', agent_id=agent_id))
            # Создание сессии
            session_id = add_session(user_id, agent_id, platform_id)
            if session_id is None:
                flash("Не удалось создать сессию. Пожалуйста, повторите попытку.", "error")
                return redirect(url_for('session_bp.assign_platform', agent_id=agent_id))
            flash(f"Сессия {session_id} успешно создана.", "success")
            # Привязка вебхука и сохранение бота
            webhook_port = get_last_webhook_port()
            add_telegram_bot(session_id, api_token, bot_name, f'@{bot_username}', webhook_port)
            flash('Бот успешно создан!', 'success')
        if platform_id in [3, 4, 5]:
            flash("Функционал ещё не реализован, вернитесь позже.", "error")
            return redirect(url_for('session_bp.assign_platform', agent_id=agent_id))

        return redirect(url_for('session_bp.sessions'))
    except Exception as e:
        flash(f"Ошибка при создании сессии: {e}", "error")
        logger.log(f"Ошибка при создании сессии: {e}", "ERROR")
        return redirect(url_for('session_bp.assign_platform', agent_id=agent_id))


@session_bp.route('/sessions', methods=['GET'])
@limiter.limit("5 per minute", key_func=custom_limit_key)
def sessions():
    """
    Отображение всех активных сессий текущего пользователя.
    Если пользователь является администратором, отображаются все сессии, кроме его собственных.
    """
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('user_bp.login'))
    try:
        user_id = session.get('user_id')
        user_sessions = get_user_sessions(user_id)
        # Если пользователь администратор, добавляем все сессии, кроме его
        all_sessions = []
        if session.get('role_id') == 1:
            all_sessions = get_all_sessions_except_admin(user_id)
        return render_template('sessions.html', user_sessions=user_sessions, all_sessions=all_sessions)
    except Exception as e:
        flash(f"Ошибка при загрузке списка сессий: {e}", "error")
        return redirect(url_for('agent_bp.agent_selection'))


@session_bp.route('/webhook/<int:session_id>', methods=['POST'])
@limiter.limit("5 per minute", key_func=custom_limit_key)
def webhook(session_id):
    """
    Обработка обновлений от Telegram.
    """
    bot_runner = bot_manager.get_bot(session_id)
    if not bot_runner:
        logger.log(f"Bot for session {session_id} not found", level="ERROR")
        return jsonify({"error": "Bot not found"}), 404
    update_data = request.get_json()
    try:
        update = create_update_from_json(update_data)
        loop = current_app.config["event_loop"]
        asyncio.run_coroutine_threadsafe(
            bot_runner.dp.feed_update(bot_runner.bot, update), loop
        )
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.log(f"Error processing webhook for session {session_id}: {str(e)}", level="ERROR")
        return jsonify({"error": str(e)}), 500


@session_bp.route('/sessions/activate/<int:session_id>', methods=['POST'])
@limiter.limit("5 per minute", key_func=custom_limit_key)
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
            port = user_session['webhook_port']
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
@limiter.limit("5 per minute", key_func=custom_limit_key)
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


@session_bp.route('/sessions/configure/<int:session_id>', methods=['GET', 'POST'])
@limiter.limit("5 per minute", key_func=custom_limit_key)
def configure_session(session_id):
    """
    Маршрут для настройки бота в сессии.
    """
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('user_bp.login'))
    if not has_access(session_id, 'session', session['user_id'], session.get('role_id')):
        flash("У вас нет прав на доступ к этой сессии.", "error")
        return redirect(url_for('session_bp.sessions'))
    try:
        user_session = get_session_by_id(session_id)
        # Настройка Telegram (ботов)
        if user_session['chat_type_id'] == 2:
            if request.method == 'GET':
                if not user_session:
                    flash("Конфигурация бота не найдена.", "error")
                    return redirect(url_for('session_bp.sessions'))
                return render_template('configure_session.html', bot_config=user_session)
            if request.method == 'POST':
                bot_name = request.form.get('bot_name')
                bot_description = request.form.get('bot_description')
                error_messages = []
                if bot_name:
                    if not update_bot_name_db(session_id, bot_name):
                        error_messages.append("Ошибка при обновлении имени бота. Не валидное имя бота.")
                if bot_description:
                    if not update_bot_description_db(session_id, bot_description):
                        error_messages.append("Ошибка при обновлении описания бота. Не валидное описание бота.")
                if error_messages:
                    flash(" ".join(error_messages), "error")
                else:
                    flash("Настройки успешно обновлены!", "success")
                return redirect(url_for('session_bp.sessions'))
        # Настройка остальных платформ
        elif user_session['chat_type_id'] in [3, 4, 5]:
            flash("Функционал ещё не реализован, вернитесь позже.", "error")
            return redirect(url_for('session_bp.sessions'))

        else:
            flash('Настройка доступна только для Telegram ботов.', 'error')
    except Exception as e:
        logger.log(f"Ошибка при настройке бота сессии {session_id}: {e}", "ERROR")
        flash(f"Ошибка: {e}", "error")
        return redirect(url_for('session_bp.sessions'))
